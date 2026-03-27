import pandas as pd

def get_top_zones(df: pd.DataFrame, metric: str, n: int = 5, direction: str = 'desc',
                  country: str = None, zone_type: str = None, week: str = 'L0W_ROLL'):

    mask = df['METRIC_NORM'] == metric
    if country:
        mask &= df['COUNTRY_NORM'] == country
    if zone_type:
        mask &= df['ZONE_TYPE'].str.lower() == zone_type.lower()

    result = df[mask][['COUNTRY', 'CITY', 'ZONE', 'ZONE_TYPE', 'ZONE_PRIORITIZATION', week]]\
        .dropna(subset=[week])\
        .sort_values(week, ascending=(direction == 'asc'))\
        .head(n)\
        .reset_index(drop=True)
    result.columns = ['COUNTRY', 'CITY', 'ZONE', 'ZONE_TYPE', 'ZONE_PRIORITIZATION', 'value']
    return result