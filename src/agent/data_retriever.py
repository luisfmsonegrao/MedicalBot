import boto3
import time
import pandas as pd
from .agent_config import AWS_REGION, ATHENA_DATABASE_NAME, ATHENA_OUTPUT_PATH

athena = boto3.client('athena',region_name=AWS_REGION)

def get_data(query):
    """Query patient data from Amazon Athena database"""

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
        raise Exception(f"Athena query failed: {state}")

    results = athena.get_query_results(QueryExecutionId=execution_id)
    columns = [col['Label'] for col in results['ResultSet']['ResultSetMetadata']['ColumnInfo']]
    rows = [
        [field.get('VarCharValue', None) for field in row['Data']]
        for row in results['ResultSet']['Rows'][1:]
    ]
    answer = {k: list(v) for k, v in zip(columns, zip(*rows))}
    return answer