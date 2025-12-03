from collections import Counter, defaultdict
#ToDo: I am implementing the same metric multiple times. DRY. make generic metric functions

def calculate_positive_rate(items, metric, values,*,group_fields=None):
    """
    Calculate positive rate for metric (metric should be binary-valued).
    e.g. Positive rate of user feedback or tastk completion
    Supports calculation per group, e.g. per task type or code version.
    """
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
    """
    Calculate mean value of metric.
    e.g. Mean query duration.
    Supports calculation per group, e.g. per task type or code version.
    """
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
    Calculate mean count of items with same value of metric.
    e.g. mean number of queries per session
    Supports calculation per group, e.g. per task type or code version.
    """
    if group_fields is None:
        group_fields = ()
    metric_name = f"MeanLength:{metric}"
    metric_data = []
    agg = aggregate_ids_and_counts(items,metric,group_fields)
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

    return metric_data

def calculate_total_count(items,metric,*,group_fields=None):
    """
    Calculate total item count per metric.
    e.g. total number of queries or sessions
    """
    if group_fields is None:
        group_fields = ()
    metric_name = f"TotalCount:{metric}"
    metric_data = []
    agg = aggregate_unique_counts(items,metric,group_fields)
    group_metrics = {}
    for (group,data) in agg.items():
        group_metrics[group] = len(data)
    for (group,metric_value) in group_metrics.items():
        metric_data.append({
            "MetricName": metric_name,
            "Dimensions": [{"Name":dim_name,"Value":dim_value} for (dim_name,dim_value) in zip(group_fields,group)],
            "Value": metric_value,
            "Unit": "Count"
        })
    return metric_data

def aggregate_pos_neg(items,metric,values,group_fields):
    """
    Aggregate positive and negative counts of (binary) metric, per group.
    e.g. count of positive and negative user feedback instances.
    """
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
    """
    Aggregate values and element counts of metric, per group.
    e.g. total duration of queries and number of queries.
    """
    agg = defaultdict(lambda: {"count":0, "value":0})
    for item in items:
        if group_fields:
            key = tuple(item[f] for f in group_fields)
        else:
            key = ("TOTAL",)
        agg[key]["count"] += 1
        agg[key]["value"] += item[metric]
    return agg

def aggregate_ids_and_counts(items,metric,group_fields):#ToDo: Refactor/Rename
    """
    Aggregate unique values of metric and total count of elemnts, per group.
    e.g. number of unique sessions and total number of queries
    """
    agg = defaultdict(lambda: {"ids":set(),"count":0})
    for item in items:
        if group_fields:
            key = tuple(item[f] for f in group_fields)
        else:
            key = ("TOTAL",)
        agg[key]["ids"].add(item[metric])
        agg[key]["count"]+=1
    return agg

def aggregate_unique_counts(items,metric,group_fields):
    """
    Aggregate count of unique values of metric, per group.
    e.g. number of unique queries or sessions
    """
    agg = defaultdict(lambda: set())
    for item in items:
        if group_fields:
            key = tuple(item[f] for f in group_fields)
        else:
            key = ("TOTAL",)
        agg[key].add(item[metric])
    return agg