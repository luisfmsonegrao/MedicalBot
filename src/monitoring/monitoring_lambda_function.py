import boto3
import time
from boto3.dynamodb.conditions import Attr
from .interaction_loader import load_data
from .metrics import calculate_positive_rate
from .config import TABLE_NAME, TIME_DELTA, NAMESPACE, MONITORING_VARIABLES

dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):   
    end_time = int(time.time())
    start_time = end_time - TIME_DELTA
    items = load_data(start_time,end_time) 
    for metric in MONITORING_VARIABLES.keys():
        metric_data = calculate_positive_rate(items,metric)
        cloudwatch.put_metric_data(
            Namespace=NAMESPACE,
            MetricData=metric_data
        )
    return {"status": "success"}