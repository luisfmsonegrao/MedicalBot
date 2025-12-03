TABLE_NAME = "medicalbot-cache"
NAMESPACE = "medicalbot/experimental"
TIME_DELTA = 3600
POSITIVE_RATE_METRICS = {'feedback': {'positive': 'positive', 'negative': 'negative'},'task_status': {'positive': True, 'negative': False}}
MEAN_COUNT_METRICS = ['session_id']
TOTAL_COUNT_METRICS = ['session_id', 'query_id']
MEAN_PER_TASK_METRICS = ['total_duration']
MEAN_METRICS= ['intent_duration','pred_duration','context_duration','qa_duration','dbquery_duration']
