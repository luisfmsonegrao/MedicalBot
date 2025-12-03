import boto3
import time
from interaction_loader import load_data
from metrics import calculate_positive_rate, calculate_mean_count, calculate_total_count, calculate_mean, calculate_mean_value
from config import TIME_DELTA, NAMESPACE, POSITIVE_RATE_METRICS, MEAN_COUNT_METRICS, TOTAL_COUNT_METRICS, MEAN_PER_TASK_METRICS, MEAN_METRICS

dynamodb = boto3.resource('dynamodb')
cloudwatch = boto3.client('cloudwatch')

def lambda_handler(event, context):
    """
    Log metrics to CloudWatch.
    """  
    end_time = int(time.time())
    start_time = end_time - TIME_DELTA
    items = load_data(start_time,end_time) 
    for metric in POSITIVE_RATE_METRICS.keys():
        version_metric_data = calculate_positive_rate(items,metric,POSITIVE_RATE_METRICS[metric],group_fields=("task_type","lambda_version"))
        if version_metric_data:
            cloudwatch.put_metric_data(
                Namespace=NAMESPACE,
                MetricData=version_metric_data
            )
        metric_data = calculate_positive_rate(items,metric,POSITIVE_RATE_METRICS[metric],group_fields=("task_type",))
        if metric_data:
            cloudwatch.put_metric_data(
                Namespace=NAMESPACE,
                MetricData=metric_data
            )
    for metric in MEAN_COUNT_METRICS:
        metric_data = calculate_mean_count(items,metric)
        if metric_data:
            cloudwatch.put_metric_data(
                Namespace=NAMESPACE,
                MetricData=metric_data
            )
    for metric in TOTAL_COUNT_METRICS:
        metric_data = calculate_total_count(items,metric)
        if metric_data:
            cloudwatch.put_metric_data(
                Namespace=NAMESPACE,
                MetricData=metric_data
            )
    for metric in MEAN_PER_TASK_METRICS:
        metric_data = calculate_mean(items,metric,group_fields=("task_type",))
        if metric_data:
            cloudwatch.put_metric_data(
                Namespace=NAMESPACE,
                MetricData=metric_data
            )
    for metric in MEAN_METRICS:
        metric_data = calculate_mean(items,metric)
        if metric_data:
            cloudwatch.put_metric_data(
                Namespace=NAMESPACE,
                MetricData=metric_data
            )
    return {"status": "success"}