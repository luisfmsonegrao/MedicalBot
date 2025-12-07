import joblib
import os
import pandas as pd
from os.path import dirname
from .agent_config import MODEL_FEATURES
from .custom_errors import ModelPredictionError
from .time_decorator import measure_duration
from langchain.tools import tool

file_path = os.path.abspath(__file__)
root_dir = dirname(dirname(dirname(file_path)))
model_path = os.path.join(root_dir,"models/COPD_Classifier")
model = joblib.load(model_path)

feature_schema = """
    - age: int
    - sex: string ("Male"/"Female")
    - smoker: string ("Yes"/"No")
    - bmi: float
"""

@tool("get_prediction",
      description=f"""Predict Chronic Obstructive Pulmonary Disease class based on the feature values extracted from the user query. 
      Required features: {feature_schema}
      If the user query has missing or invalid feature values, attribute None value to those features.""")
def get_prediction(features):
    """
    Predict Chronic Obstructive Pulmonary Disease class based on feature values.
    """
    print(features)
    status, missing_features = validate_features(features)
    if not status:
        return f"Please specify values of features: {missing_features}"
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