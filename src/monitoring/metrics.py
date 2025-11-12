from config import POSITIVE_RATE_METRICS
from collections import Counter


def calculate_positive_rate(items,metric):
    """
    Calculate positive rate for binary metrics
    """
    metric_name = f"PositiveRate:{metric}"
    metric_counts = {}
    for item in items:
        task_type = item.get("task_type", "Unknown")
        metric_value = item.get(metric, "NA")
        
        if task_type not in metric_counts:
            metric_counts[task_type] = {"positive": 0, "negative": 0}
        
        if metric_value == POSITIVE_RATE_METRICS[metric]['positive']:
            metric_counts[task_type]["positive"] += 1
        elif metric_value == POSITIVE_RATE_METRICS[metric]['negative']:
            metric_counts[task_type]["negative"] += 1

    metric_data = []
    for task_type, counts in metric_counts.items():
        pos = counts["positive"]
        neg = counts["negative"]
        
        if pos + neg == 0:
            positive_rate = 0 # ToDo> Change this to enable distinguishing bad metrics from zero usage.
        else:
            positive_rate = (pos / (pos + neg)) * 100
        
        metric_data.append({
            "MetricName": metric_name,
            "Dimensions": [{"Name": "TaskType", "Value": task_type}],
            "Value": positive_rate,
            "Unit": "Percent"
        })
    return metric_data

def calculate_mean_count(items,metric):
    """
    Calculate the mean count per distinct value of metric
    """
    counts = Counter()
    for item in items:
        value = item.get(metric)
        if value:
            counts[value] += 1
    if not counts:
        return 0
    total_counts = sum(counts.values())
    total_values = len(counts)
    return total_counts / total_values