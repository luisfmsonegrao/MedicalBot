from src.monitoring.metrics import aggregate_pos_neg

def test_pos_neg_agg():
    items = [{'status':'negative','feedback':'negative'},
             {'status':'negative','feedback':'positive'},
             {'status':'negative','feedback':'positive'},
             {'status':'negative','feedback':'positive'}]
    metric = 'feedback'
    values = {'positive':'positive','negative':'negative'}
    group_fields = ()
    agg = aggregate_pos_neg(items,metric,values,group_fields)
    assert len(agg.keys()) == 1
    assert ("TOTAL",) in agg
    assert agg[("TOTAL",)]["positive"] == 3
    assert agg[("TOTAL",)]["negative"] == 2



    