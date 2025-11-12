from json import JSONDecodeError

class AthenaQueryError(Exception):
    def __init__(self, state, reason, error_type, error_category):
        super().__init__(f"Athena query failed ({state}):\nReason: {reason}\n Error Category: {error_category}\n Error Type: {error_type}")

class ModelPredictionError(Exception):
    def __init__(self, original_exception):
        super().__init__(f"Model Prediction failed:\n Reason: {type(original_exception).__name__}\n Message: {str(original_exception)}")

class LLMJSONError(JSONDecodeError):
    def __init__(self, task_type, original_exception):
        self.task_type = task_type
        super().__init__(f"LLM generated invalid JSON:\n Reason: {type(original_exception).__name__}\n Message: {str(original_exception)}")
