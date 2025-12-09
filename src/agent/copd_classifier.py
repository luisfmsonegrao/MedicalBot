import joblib
import os
from os.path import dirname
import pandas as pd
from .agent_config import MODEL_FEATURES
from .custom_errors import ModelPredictionError
from .tool_input_models import PredictionInput


file_path = os.path.abspath(__file__)
root_dir = dirname(dirname(dirname(file_path)))
model_path = os.path.join(root_dir,"models/COPD_Classifier")
model = joblib.load(model_path)

def predict_copd(features: PredictionInput):
    """
    Predict Chronic Obstructive Pulmonary Disease class based on feature values.
    """
    status, missing_features = validate_features(features)
    if not status:
        return f"Prompt the user to provide valid values for features {missing_features}."
    
    X = pd.DataFrame([features.model_dump()])
    try:
        pred = model.predict(X)
        answer = f"Chronic Obstructive Pulmonary disease class {pred[0]}"
    except Exception as e:
        raise ModelPredictionError(e)
    return answer

def validate_features(features):
    """
    Check if all necessary features are present
    """
    status = True
    missing_features = [f for f in MODEL_FEATURES if getattr(features,f) in (None,"","null")]
    if missing_features:
        status = False
    return status, missing_features