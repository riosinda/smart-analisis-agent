import pandas as pd

def find_zones_multi_criteria(df: pd.DataFrame, criteria: list):
    pivot = df.pivot_table(
        index=['COUNTRY','CITY','ZONE','ZONE_TYPE','ZONE_PRIORITIZATION'],
        columns='METRIC',
        values='L0W_ROLL'
    )
    pivot.columns.name = None
    
    base_mask = pd.Series([True] * len(pivot), index=pivot.index)

    for c in criteria:
        metric = c['metric']
        direction = c['direction']  # 'high' o 'low'
        pct = c.get('threshold_pct', 0.75 if direction == 'high' else 0.25)

        if metric not in pivot.columns:
            print(f"  ⚠ Métrica '{metric}' no encontrada")
            continue

        threshold = pivot[metric].quantile(pct)
        if direction == 'high':
            base_mask &= pivot[metric] >= threshold
        else:
            base_mask &= pivot[metric] <= threshold

    result = pivot[base_mask].reset_index()

    id_cols = ['COUNTRY', 'CITY', 'ZONE', 'ZONE_TYPE', 'ZONE_PRIORITIZATION']
    metric_cols = [c['metric'] for c in criteria if c['metric'] in pivot.columns]

    return result[id_cols + metric_cols].round(4)