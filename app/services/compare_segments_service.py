import pandas as pd

def compare_segments(df: pd.DataFrame, metric: str, group_by: str, filters: dict = {}):

    mask = df['METRIC_NORM'] == metric
    for col, val in filters.items():
        mask &= df[col] == val

    result = df[mask].groupby(group_by)['L0W_ROLL'].agg(
        zonas='count',
        promedio='mean',
        mediana='median',
        p25=lambda x: x.quantile(0.25),
        p75=lambda x: x.quantile(0.75),
        minimo='min',
        maximo='max'
    ).round(4)
    return result

