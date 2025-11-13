import boto3
import time
import pandas as pd
from .agent_config import AWS_REGION, ATHENA_DATABASE_NAME, ATHENA_OUTPUT_PATH
from .custom_errors import AthenaQueryError
from .time_decorator import measure_duration
athena = boto3.client('athena',region_name=AWS_REGION)

@measure_duration
def get_data(query):
    """
    Query patient data from Amazon Athena database
    """

    response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={'Database': ATHENA_DATABASE_NAME},
        ResultConfiguration={'OutputLocation': ATHENA_OUTPUT_PATH}
    )
    execution_id = response['QueryExecutionId']

    while True:
        status = athena.get_query_execution(QueryExecutionId=execution_id)
        state = status['QueryExecution']['Status']['State']
        if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        time.sleep(0.5)

    if state != 'SUCCEEDED':
        status_info = status['QueryExecution']['Status']
        reason = status_info.get('StateChangeReason', 'Unknown reason')
        athena_error = status_info.get('AthenaError','')
        error_type = athena_error.get('ErrorType','')
        error_category = athena_error.get('ErrorCategory','')
        raise AthenaQueryError(
            state=state,
            reason=reason,
            error_type=error_type,
            error_category=error_category,
        )

    results = athena.get_query_results(QueryExecutionId=execution_id)
    columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    rows = [
        [field.get('VarCharValue', None) for field in row['Data']]
        for row in results['ResultSet']['Rows'][1:]
    ]
    answer = {k: list(v) for k, v in zip(columns, zip(*rows))}
    return answer