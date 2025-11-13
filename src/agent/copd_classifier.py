import joblib
import os
import pandas as pd
from os.path import dirname
from .agent_config import MODEL_FEATURES
from .custom_errors import ModelPredictionError

file_path = os.path.abspath(__file__)
root_dir = dirname(dirname(dirname(file_path)))
model_path = os.path.join(root_dir,"models\\COPD_Classifier")
model = joblib.load(model_path)

def get_prediction(features):
    """
    Predict Chronic Obstructive Pulmonary Disease class based on user's query
    """
    X = pd.DataFrame({k: [v] for k, v in features.items()})
    try:
        pred = model.predict(X)
    except Exception as e:
        raise ModelPredictionError(e)
    return pred

def validate_features(features):
    """
    Check if all necessary features are present
    """
    status = True
    missing_features = [f for f in MODEL_FEATURES if features.get(f) in (None, "", "null")]
    if missing_features:
        status = False
    return status, missing_features