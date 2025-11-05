
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import io
import boto3
import joblib
import os

target_name = 'chronic_obstructive_pulmonary_disease'
bucket_name = "lneg-loka"
data_file_name = "patient_data_raw/patient_data_raw.csv"
model_features =['age','bmi','smoker','sex','chronic_obstructive_pulmonary_disease']

s3 = boto3.client('s3')
obj = s3.get_object(Bucket=bucket_name, Key=data_file_name)
csv_string = obj['Body'].read().decode('utf-8')
data = pd.read_csv(io.StringIO(csv_string))

df = data[model_features]
X = df.drop(target_name, axis=1)
y = df[target_name]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.1, random_state=42
)

#transformation-modelling pipeline
model = DecisionTreeClassifier(
    criterion='entropy',
    max_depth=5,
    random_state=42
)
preprocessor = ColumnTransformer(transformers=[('cat',OneHotEncoder(drop='first'),['sex','smoker'])],remainder='passthrough')
pipe = Pipeline([("preprocess",preprocessor),("model", model)])

#fit
pipe.fit(X_train,y_train)

#predict
y_pred = pipe.predict(X_test)

print("Accuracy:", accuracy_score(y_test, y_pred)) 
print("Classification Report:\n", classification_report(y_test, y_pred))
plt.figure(figsize=(20,10))
tree.plot_tree(model, feature_names=X.columns, class_names=True, filled=True)
plt.show()
model_dir = '.\..\models'
model_name = 'decision_tree_classifier.joblib'
joblib.dump(pipe,os.path.join(model_dir,model_name))


