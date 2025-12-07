import boto3
import time
from .agent_config import AWS_REGION, ATHENA_DATABASE_NAME, ATHENA_OUTPUT_PATH, PATIENT_DATA_TABLE_NAME
from .custom_errors import AthenaQueryError
from .time_decorator import measure_duration
from .table_schema_retriever import get_table_schema
from langchain.tools import tool

table_schema = get_table_schema(ATHENA_DATABASE_NAME,PATIENT_DATA_TABLE_NAME)
athena = boto3.client('athena',region_name=AWS_REGION)

@tool("get_data", description=f"""Query data from Amazon Athena table {PATIENT_DATA_TABLE_NAME}. Strictly obey the table schema: {table_schema}. If there are variables not in the table schema, don't use them.""")
def get_data(query):
    """
    Query patient data from Amazon Athena database
    """

    print(query)
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