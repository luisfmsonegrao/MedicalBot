import joblib
import os
import pandas as pd
from os.path import dirname
from .agent_config import MODEL_FEATURES
from .custom_errors import ModelPredictionError
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

tool_name = "make_prediction"
tool_description =f"""Use {tool_name} to predict the class of Chronic Obstructive Pulmonary Disease based on the features extracted from the user query. Feature schema: {feature_schema}.
                      Don't use the tool if there are missing or invalid feature values. Instead, prompt user to provide those values. """

@tool(tool_name, description=tool_description)
def make_prediction(features):
    """
    Predict Chronic Obstructive Pulmonary Disease class based on feature values.
    """
    status, missing_features = validate_features(features)
    if not status:
        return f"Prompt the user to provide valid values for features {missing_features}."
    
    X = pd.DataFrame({k: [v] for k, v in features.items()})
    try:
        pred = model.predict(X)
        answer = f"Predicted class of Chronic Obstructive Pulmonary disease: {pred[0]}"
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