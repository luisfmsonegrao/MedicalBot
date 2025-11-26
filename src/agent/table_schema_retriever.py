import boto3
from .agent_config import AWS_REGION

def get_table_schema(database, table):
    """
    Retrieve patient data Amazon Athena table schema
    """
    
    glue = boto3.client('glue',region_name=AWS_REGION)
    response = glue.get_table(DatabaseName=database, Name=table)
    cols = response['Table']['StorageDescriptor']['Columns']
    return "\n".join([f"{c['Name']}: {c['Type']}" for c in cols])