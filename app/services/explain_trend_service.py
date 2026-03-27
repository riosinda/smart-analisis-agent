import pandas as pd

ROLL_COLS = ['L8W_ROLL','L7W_ROLL','L6W_ROLL','L5W_ROLL','L4W_ROLL','L3W_ROLL','L2W_ROLL','L1W_ROLL','L0W_ROLL']

def explain_trend(df: pd.DataFrame, n_weeks: int = 5, top_n: int = 10, filters: dict = {}):
    
    start_col = ROLL_COLS[-(n_weeks + 1)]  # semana de inicio
    end_col   = 'L0W_ROLL'

    mask = df[start_col].notna() & df[end_col].notna()
    for col, val in filters.items():
        mask &= df[col] == val

    base = df[mask].copy()
    base['growth_abs'] = base[end_col] - base[start_col]
    base['growth_pct'] = (base['growth_abs'] / base[start_col].abs()) * 100

    # Top zonas crecientes por métrica
    top_growing = base.sort_values('growth_pct', ascending=False)\
        [['COUNTRY','CITY','ZONE','METRIC', start_col, end_col, 'growth_pct']]\
        .head(top_n).round(3)

    # Para las zonas top, ver si otras métricas también crecieron (posible causa)
    top_zones = top_growing['ZONE'].unique()
    related = df[df['ZONE'].isin(top_zones)]\
        .groupby(['ZONE','METRIC'])['growth_pct'].first() if 'growth_pct' in df.columns else None

    return top_growing