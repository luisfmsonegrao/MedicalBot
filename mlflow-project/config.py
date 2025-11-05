import os

MLFLOW_TRACKING_PATH = os.path.abspath(os.path.join(os.getcwd(),os.path.pardir,'mlruns'))
MODEL_NAME = "COPD_Classifier"
DEPLOY_PATH = os.path.abspath(os.path.join(os.getcwd(),os.path.pardir,"models"))
EXPERIMENT_NAME = "COPD_classifier_experiments"
S3_BUCKET_NAME = "lneg-loka"
S3_DATA_FILENAME = "patient_data_raw/patient_data_raw.csv"

