from config import POSITIVE_RATE_METRICS
from collections import Counter

#ToDo: I am implementing the same metric multiple times. DRY. make generic metric functions

def calculate_positive_rate_per_task(items,metric):
    """
    Calculate positive rate for binary metrics, per task type.
    e.g. positive rate of user feedback or task completion
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

def calculate_mean_per_task(items,metric):
    """
    Calculate mean value of metric, per task type.
    e.g. mean duration of question answering tasks
    """
    metric_name = f"Mean:{metric}"
    metric_sums = {}
    metric_data = []
    for item in items:
        task_type = item.get("task_type")
        if task_type not in metric_sums:
            metric_sums[task_type] = {'count':0, 'value':0}
        metric_sums[task_type]['count'] += 1
        metric_sums[task_type]['value'] += float(item.get(metric))

    for task_type,v in metric_sums.items():
        mean_value = v['value']/v['count']
        metric_data.append({
            "MetricName": metric_name,
            "Dimensions": [{"Name": "TaskType", "Value": task_type}],
            "Value": mean_value,
            "Unit": "Seconds"
        })
    return metric_data

def calculate_mean_durations(items, metric):
    """
    Calculate mean value of metric.
    e.g. mean duration of athena data retrieval
    """
    metric_name = f"Mean:{metric}"
    metric_data = []
    metric_sum = 0
    metric_count = 0
    for item in items:
        if item[metric] != 0: # durations will only be zero if corresponding tasks are not run, or task fails.
            metric_sum += item[metric]
            metric_count += 1
    if metric_count != 0:
        mean_value = metric_sum / metric_count
    else:
        mean_value = 0
    metric_data.append({
        "MetricName": metric_name,
        "Value": mean_value,
        "Unit": "Seconds"
    })
    return metric_data



def calculate_mean_count(items,metric):
    """
    Calculate mean count per distinct value of metric.
    e.g. mean number of queries per session
    """
    metric_name = f"MeanLength:{metric}"
    metric_data = []
    counts = Counter()
    for item in items:
        value = item.get(metric)
        if value:
            counts[value] += 1
    if not counts:
        metric_data.append({
            "MetricName": metric_name,
            "Value": 0,
            "Unit": "Count"
        })
        return metric_data
    
    total_counts = sum(counts.values())
    total_values = len(counts)
    mean_count = total_counts / total_values
    metric_data.append({
            "MetricName": metric_name,
            "Value": mean_count,
            "Unit": "Count"
        })
    return metric_data

def calculate_total_count(items,metric):
    """
    Calculate total count per metric.
    e.g. total number of queries or sessions
    """
    metric_name = f"TotalCount:{metric}"
    metric_data = []
    values = {item[metric] for item in items if metric in item}
    count = len(values)
    metric_data.append({
            "MetricName": metric_name,
            "Value": count,
            "Unit": "Count"
        })
    return metric_data