import boto3
import time
from boto3.dynamodb.conditions import Attr

dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

TABLE_NAME = "medicalbot-cache"
NAMESPACE = "medicalbot/feedback"

time_delta = 3600

table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):   
    end_time = int(time.time())
    start_time = end_time - time_delta
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
    
    feedback_counts = {}
    for item in items:
        task_type = item.get("task_type", "Unknown")
        feedback = item.get("feedback", "NA")
        
        if task_type not in feedback_counts:
            feedback_counts[task_type] = {"positive": 0, "negative": 0}
        
        if feedback == "positive":
            feedback_counts[task_type]["positive"] += 1
        elif feedback == "negative":
            feedback_counts[task_type]["negative"] += 1

    metric_data = []
    for task_type, counts in feedback_counts.items():
        pos = counts["positive"]
        neg = counts["negative"]
        
        if pos + neg == 0:
            continue
        
        positive_rate = (pos / (pos + neg)) * 100
        
        metric_data.append({
            "MetricName": "PositiveFeedbackRate",
            "Dimensions": [{"Name": "TaskType", "Value": task_type}],
            "Value": positive_rate,
            "Unit": "Percent"
        })
         
    if metric_data:
        cloudwatch.put_metric_data(
            Namespace=NAMESPACE,
            MetricData=metric_data
        )
    else:
        print("No feedback data found in the last hour.")

    return {"status": "success", "metrics_published": len(metric_data)}