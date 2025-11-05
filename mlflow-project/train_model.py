import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
import io
import boto3
import mlflow
import argparse
from config import S3_BUCKET_NAME, S3_DATA_FILENAME

hyperparameters = ["max_depth","criterion"]
s3 = boto3.client('s3')
model_features =['age','bmi','smoker','sex','chronic_obstructive_pulmonary_disease']
one_hot_features = ['sex','smoker']
target_name = 'chronic_obstructive_pulmonary_disease'
test_data_ratio = 0.1

parser = argparse.ArgumentParser()
parser.add_argument("--max_depth", type=int, required=False, default=3)
parser.add_argument("--criterion", type=str, required=False, default="gini")


#load data
def load_data():
    obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=S3_DATA_FILENAME)
    csv_string = obj['Body'].read().decode('utf-8')
    data = pd.read_csv(io.StringIO(csv_string))
    return data

#Filter model features and target
def filter_data(data):
    y = data[target_name]
    X = data[model_features]
    X = X.drop(target_name, axis=1)
    return X, y

#Split data into training and test set
def split_data(X,y):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_data_ratio, random_state=42
    )
    return X_train, X_test, y_train, y_test

#Build model pipeline
def build_model(args):
    model = DecisionTreeClassifier(
        criterion=args.criterion,
        max_depth=args.max_depth,
        random_state=42
    )
    #Build data preprocessing
    preprocessor = ColumnTransformer(transformers=[('cat',OneHotEncoder(drop='first'),one_hot_features)],remainder='passthrough')
    #Build model pipeline
    pipe = Pipeline([("preprocess",preprocessor),("model", model)])
    return pipe

#Train model, save to mlflow
def run_experiment(model,train_features,train_targets,test_features,test_targets):
    max_depth = model.named_steps['model'].get_params()['max_depth']
    criterion = model.named_steps['model'].get_params()['criterion']
    model.fit(train_features,train_targets)
    y_pred = model.predict(test_features)
    accuracy = accuracy_score(test_targets,y_pred)
    mlflow.log_metric("accuracy",accuracy)
    mlflow.log_param('max_depth',max_depth)
    mlflow.log_param('criterion',criterion)
    mlflow.sklearn.log_model(model,name="model",input_example = train_features.head(1))


if __name__ == "__main__":
    args = parser.parse_args()
    if all(hasattr(args,param) for param in hyperparameters):
        data = load_data()
        X, y = filter_data(data)
        X_train, X_test, y_train, y_test = split_data(X,y)
        model_pipeline = build_model(args)
        run_experiment(model_pipeline,X_train,y_train,X_test,y_test)
