import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import tree
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt
import io
import boto3
import joblib
import os

#load preprocessed data
bucket_name = "lneg-loka"
file_name = "patient_data_processed.csv"
s3 = boto3.client('s3')
obj = s3.get_object(Bucket=bucket_name, Key=file_name)
csv_string = obj['Body'].read().decode('utf-8')
data = pd.read_csv(io.StringIO(csv_string))

#Not sure why this column is being added to dataframe. ToDo:Investigate
data=data.drop('Unnamed: 0',axis=1)

#Prepare data for training model
target_column = 'chronic_obstructive_pulmonary_disease'
X = data.drop(target_column, axis=1)
y = data[target_column]
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.1, random_state=42
)

#Train decision tree classifier model
#ToDo: add hyperparameter tuning, pruning, others
model = DecisionTreeClassifier(
    criterion='entropy',
    max_depth=5,
    random_state=42
)
model.fit(X_train,y_train)

#save model for later use
model_dir = '.\..\models'
model_name = 'decision_tree_classifier.joblib'
joblib.dump(model,os.path.join(model_dir,model_name))



