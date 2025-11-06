import joblib
import os
import pandas as pd
from os.path import dirname
from .agent_config import MODEL_FEATURES

file_path = os.path.abspath(__file__)
root_dir = dirname(dirname(dirname(file_path)))
model_path = os.path.join(root_dir,"models\\COPD_Classifier")
model = joblib.load(model_path)

def get_prediction(features):
    """Predict Chronic Obstructive Pulmonary Disease class based on user's query"""

    missing = [f for f in MODEL_FEATURES if features.get(f) in (None, "", "null")]
    if missing:
            return f"Missing required features: {missing}. Please provide them in your query."
    X = pd.DataFrame({k: [v] for k, v in features.items()})
    pred = model.predict(X)
    return pred