import boto3
from boto3.dynamodb.conditions import Attr
from .config import TABLE_NAME

dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')
table = dynamodb.Table(TABLE_NAME)

def load_data(start_time, end_time):
    """
    Load interactions within timeframe from DynamoDB
    """
    response = table.scan(
        FilterExpression=Attr("timestamp").between(start_time,end_time)
    )
    items = response["Items"]
    
    while "LastEvaluatedKey" in response:
        response = table.scan(
            FilterExpression=Attr("timestamp").between(start_time, end_time),
            ExclusiveStartKey=response["LastEvaluatedKey"]
        )
        items.extend(response["Items"])

    return items