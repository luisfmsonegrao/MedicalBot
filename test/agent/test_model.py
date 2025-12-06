from src.agent.copd_classifier import get_prediction

def test_get_prediction():
    valid_features = {"age":22,"sex":"Female","smoker":"Yes","bmi":18}
    prediction,_ = get_prediction(valid_features)
    classes = ['A','B','C','D']
    assert prediction.__class__.__name__ == "ndarray"
    assert prediction[0] in classes

