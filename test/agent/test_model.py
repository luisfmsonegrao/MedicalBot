from src.agent.copd_classifier import predict_copd
from src.agent.tool_input_models import PredictionInput

def test_get_prediction():
    valid_features = PredictionInput(age=22,sex="Female",smoker="Yes",bmi=19)
    prediction = predict_copd(valid_features)
    classes = ['A','B','C','D']
    assert len(prediction) == 1
    assert prediction.__class__.__name__ == "ndarray"
    assert prediction[0] in classes

