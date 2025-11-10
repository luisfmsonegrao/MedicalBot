class AthenaQueryError(Exception):
    def __init__(self, state, reason, athena_error, error_type, error_category):
        self.state = state
        self.reason = reason
        self.athena_error = athena_error
        self.error_type = error_type
        self.error_category = error_category
        super().__init__(f"Athena query failed ({state}):\nReason: {reason}\n Error Category: {error_category}\n Error Type: {error_type}")