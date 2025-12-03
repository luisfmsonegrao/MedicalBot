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

def aggregate_values(items,metric,group_fields):
    agg = defaultdict(lambda: {"count":0, "value":0})
    for item in items:
        if group_fields:
            key = tuple(item[f] for f in group_fields)
        else:
            key = ("TOTAL",)
        agg[key]["count"] += 1
        agg[key]["value"] += item[metric]
    return agg

def aggregate_counts(items,metric,group_fields):
    agg = defaultdict(lambda: {"ids":set(),"count":0})
    for item in items:
        if group_fields:
            key = tuple(item[f] for f in group_fields)
        else:
            key = ("TOTAL",)
        agg[key]["ids"].add(items[metric])
        agg[key]["count"]+=1
    return agg


def calculate_positive_rate(items, metric, values,*,group_fields=None):
    if group_fields is None:
        group_fields = ()
    metric_name = f"PositiveRate:{metric}"
    metric_data = []
    agg = aggregate_pos_neg(items,metric,values,group_fields)
    group_metrics = {}
    for (group,data) in agg.items():
        try:
            group_metrics[group] = data["positive"]/(data["positive"]+data["negative"])
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

def calculate_mean(items,metric,*,group_fields=None):
    if group_fields is None:
        group_fields = ()
    metric_name = f"Mean:{metric}"
    metric_data = []
    agg = aggregate_values(items,metric,group_fields)
    group_metrics = {}
    for (group,data) in agg.items():
        try:
            group_metrics[group] = data["value"]/(data["count"])
        except ZeroDivisionError as e:
            continue
    for (group,metric_value) in group_metrics.items():
        metric_data.append({
            "MetricName": metric_name,
            "Dimensions": [{"Name":dim_name,"Value":dim_value} for (dim_name,dim_value) in zip(group_fields,group)],
            "Value": metric_value,
            "Unit": "Seconds"
        })
    return metric_data

def calculate_mean_length(items,metric,*,group_fields=None):
    """
    Calculate mean count per distinct value of metric.
    e.g. mean number of queries per session
    """
    if group_fields is None:
        group_fields = ()
    metric_name = f"MeanLength:{metric}"
    metric_data = []
    agg = aggregate_counts(items,metric,group_fields)
    group_metrics = {}
    for (group,data) in agg.items():
        try:
            group_metrics[group] = data["count"]/len(data["ids"])
        except ZeroDivisionError as e:
            continue
    for (group,metric_value) in group_metrics.items():
        metric_data.append({
            "MetricName": metric_name,
            "Dimensions": [{"Name":dim_name,"Value":dim_value} for (dim_name,dim_value) in zip(group_fields,group)],
            "Value": metric_value,
            "Unit": "Count"
        })

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