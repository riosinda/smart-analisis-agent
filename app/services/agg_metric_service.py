import pandas as pd

def aggregate_metric(df: pd.DataFrame, metric: str, group_by: str | list, agg_func: str = 'mean', filters: dict = {}):
    mask = df['METRIC_NORM'] == metric
    for col, val in filters.items():
        mask &= df[col] == val

    agg_map = {'mean': 'mean', 'median': 'median', 'sum': 'sum', 'count': 'count'}
    result = df[mask].groupby(group_by)['L0W_ROLL']\
        .agg(agg_map.get(agg_func, 'mean'))\
        .round(4)\
        .sort_values(ascending=False)\
        .reset_index()
    result.columns = [group_by, f'{agg_func}_{metric}'] if isinstance(group_by, str) else list(result.columns)
    return result