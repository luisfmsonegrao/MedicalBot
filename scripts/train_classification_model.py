
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

# ToDo: Should make preprocessing a part of model pipeline to avoid having to preprocess test data at inference time

bucket_name = "lneg-loka"
file_name = "patient_data_raw.csv"
processed_file_name = "patient_data_processed.csv"
s3 = boto3.client('s3')
obj = s3.get_object(Bucket=bucket_name, Key=processed_file_name)
csv_string = obj['Body'].read().decode('utf-8')
data = pd.read_csv(io.StringIO(csv_string))
data=data.drop('Unnamed: 0',axis=1) #Unsure why this column is being added, investigate.

target_name = 'chronic_obstructive_pulmonary_disease'
X = data.drop(target_name, axis=1)
y = data[target_name]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.1, random_state=42
)


# DecisionTree is a suitable first approach for tabular data. Class-conditional feature plots and statistical tests suggest features are not informative for prediction of Chronic Obstructive Pulmonary Disease, so I didn't bother with cross-validation or hyperparameter tuning.
model = DecisionTreeClassifier(
    criterion='entropy',
    max_depth=5,
    random_state=42
)
model.fit(X_train,y_train)

y_pred = model.predict(X_test)

print("Accuracy:\n", accuracy_score(y_test, y_pred)) 
print("Classification Report:\n", classification_report(y_test, y_pred))

plt.figure(figsize=(20,10))
tree.plot_tree(model, feature_names=X.columns, class_names=True, filled=True)
plt.show()

model_dir = '.\..\models'
model_name = 'decision_tree_classifier.joblib'
joblib.dump(model,os.path.join(model_dir,model_name))

model_copy = joblib.load(os.path.join(model_dir,model_name))
model_copy

# Train a smaller model to serve in actual AI agent application. Since all features are non-informative anyway, might as well simplify feature retrieval from user natural language query
model_features =['age','bmi','smoker_Yes','sex_Male','chronic_obstructive_pulmonary_disease']
small_data = data[model_features]
small_data
target_name = 'chronic_obstructive_pulmonary_disease'
X_small = small_data.drop(target_name, axis=1)
y_small = small_data[target_name]
X_small_train, X_small_test, y_small_train, y_small_test = train_test_split(
    X_small, y_small, test_size=0.1, random_state=42
)
model_small = DecisionTreeClassifier(
    criterion='entropy',
    max_depth=5,
    random_state=42
)
model_small.fit(X_small_train,y_small_train)
model_dir = '.\..\models'
model_small_name = 'decision_tree_classifier_small.joblib'
joblib.dump(model_small,os.path.join(model_dir,model_small_name))


