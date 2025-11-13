TABLE_NAME = "medicalbot-cache"
NAMESPACE = "medicalbot/monitoring"
TIME_DELTA = 3600
POSITIVE_RATE_METRICS = {'feedback': {'positive': 'positive', 'negative': 'negative'},'task_status': {'positive': True, 'negative': False}}
MEAN_COUNT_METRICS = ['session_id']
TOTAL_COUNT_METRICS = ['session_id', 'query_id']
MEAN_METRICS = ['duration']
