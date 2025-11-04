import joblib
from src.config import MODEL_FEATURES

model = joblib.load(".\..\..\models\decision_tree_classifier_small.joblib")

def get_prediction(features):
    """Predict Chronic Obstructive Pulmonary Disease class based on user's query"""

    missing = [f for f in MODEL_FEATURES if features.get(f) in (None, "", "null")]
    if missing:
            return f"Missing required features: {missing}. Please provide them in your query."
    X = [[float(v) for (k,v) in features.items()]]
    pred = model.predict(X)
    return pred