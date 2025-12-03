from config import POSITIVE_RATE_METRICS
from collections import Counter, defaultdict

#ToDo: I am implementing the same metric multiple times. DRY. make generic metric functions

def aggregate_pos_neg(items,metric,values,group_fields):
    agg = defaultdict(lambda: {k: 0 for k in values.keys()})
    for item in items:
        if group_fields:
            key = tuple(item[f] for f in group_fields)
        else:
            key = ("TOTAL",)
        if item[metric] == values['positive']:
            agg[key]["positive"] += 1
        elif item[metric] == values['negative']:
            agg[key]["negative"] += 1
    return agg


def calculate_positive_rate(items, metric, values, group_fields=None):
    if group_fields is None:
        group_fields = ()
    metric_name = f"PositiveRate:{metric}"
    metric_data = []
    agg = aggregate_pos_neg(items,metric,values,group_fields)
    group_metrics = {}
    for (group,counts) in agg.items():
        try:
            group_metrics[group] = counts["positive"]/(counts["positive"]+counts["negative"])
        except ZeroDivisionError as e:
            continue

    for (group,metric_value) in group_metrics.items():
        metric_data.append({
            "MetricName": metric_name,
            "Dimensions": [{"Name":dim_name,"Value":dim_value} for (dim_name,dim_value) in zip(group_fields,group)],
            "Value": metric_value,
            "Unit": "Percent"
        })
    return metric_data

def calculate_mean_per_task(items,metric):
    """
    Calculate mean value of metric, per task type.
    e.g. mean duration of question answering tasks
    """
    metric_name = f"Mean:{metric}"
    metric_agg = {}
    metric_data = []
    for item in items:
        version = item.get("lambda_version","Unknown")
        if version not in metric_agg: 
            metric_agg[version] = {}
        task_type = item.get("task_type")
        if task_type not in metric_agg[version]:
            metric_agg[version][task_type] = {'count':0, 'value':0}
        metric_agg[version][task_type]['count'] += 1
        metric_agg[version][task_type]['value'] += float(item.get(metric))

    for version, data in metric_agg.items():
        for task_type, values in data.items():
            mean_value = values['value']/values['count']
            metric_data.append({
                "MetricName": metric_name,
                "Dimensions": [
                    {"Name": "lambda_version", "Value": version},
                    {"Name": "task_type", "Value": task_type}
                    ],
                "Value": mean_value,
                "Unit": "Seconds"
            })
    return metric_data

def calculate_mean_value(items, metric):
    """
    Calculate mean value of metric.
    e.g. mean duration of athena data retrieval
    """
    metric_name = f"Mean:{metric}"
    metric_agg={}
    metric_data = []
    for item in items:
        version = item.get("lambda_version","unknown")
        if version not in metric_agg:
            metric_agg[version]={"count": 0,"value":0}
        value = item.get(metric)
        if value != 0: # durations will only be zero if corresponding tasks are not run, or task fails.
            metric_agg[version]["value"] += value
            metric_agg[version]["count"] += 1
    
    for version, data in metric_agg.items():
        if data["count"] != 0:
            metric_value = data["value"] / data["count"]
        else:
            metric_value = 0
        metric_data.append({
            "MetricName": metric_name,
            "Dimensions": [
                {"Name": "lambda_version", "Value": version}
            ],
            "Value": metric_value,
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
    metric_agg = {}
    for item in items:
        version = item.get("lambda_version","unknown")
        if version not in metric_agg:
            metric_agg[version] = Counter()
        value = item.get(metric)
        metric_agg[version][value] += 1
    
    for version, counts in metric_agg.items():
        total_counts = sum(counts.values())
        total_values = len(counts)
        mean_count = total_counts / total_values
        metric_data.append({
                "MetricName": metric_name,
                "Dimensions": [
                    {"Name": "lambda_version", "Value": version}
                ],
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
    metric_agg = {}
    metric_data = []
    for item in items:
        version = item.get("lambda_version","unknown")
        if version not in metric_agg:
            metric_agg[version] = set()
        metric_agg[version].add(item.get(metric))

    for version, elements in metric_agg.items():
        count = len(elements)
        metric_data.append({
                "MetricName": metric_name,
                "Dimensions": [
                    {"Name": "lamdba_version", "Value": version}
                ],
                "Value": count,
                "Unit": "Count"
            })
    return metric_data