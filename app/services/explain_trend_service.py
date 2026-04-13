import unicodedata

import pandas as pd

ROLL_COLS = ['L8W_ROLL', 'L7W_ROLL', 'L6W_ROLL', 'L5W_ROLL',
             'L4W_ROLL', 'L3W_ROLL', 'L2W_ROLL', 'L1W_ROLL', 'L0W_ROLL']


def _normalize(text: str) -> str:
    text = str(text).lower().strip()
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def explain_trend(
    df: pd.DataFrame,
    n_weeks: int = 5,
    top_n: int = 10,
    direction: str = "top",
    country: str = None,
    metric: str = None,
    zone_type: str = None,
    zone_prioritization: str = None,
) -> pd.DataFrame:
    """
    Devuelve las zonas con mayor crecimiento ("top") o mayor caída ("bottom")
    en las últimas n_weeks semanas, medido como variación porcentual.

    Args:
        df: DataFrame con columnas ROLL y columnas *_NORM ya generadas.
        n_weeks: Ventana de semanas (1–8). Default 5.
        top_n: Número de zonas a retornar. Default 10.
        direction: "top" = mayor crecimiento, "bottom" = mayor caída.
        country: Filtro por país (valor libre, se normaliza internamente).
        metric: Filtro por métrica (valor libre, se normaliza internamente).
        zone_type: Filtro por tipo de zona ("Wealthy" / "Non Wealthy").
        zone_prioritization: Filtro por priorización ("High Priority", etc.).

    Returns:
        DataFrame con columnas:
        COUNTRY, CITY, ZONE, METRIC, <start_col>, L0W_ROLL, growth_abs, growth_pct
        ordenado por growth_pct según direction.
    """
    n_weeks = min(max(n_weeks, 1), 8)
    start_col = ROLL_COLS[-(n_weeks + 1)]
    end_col = 'L0W_ROLL'

    mask = df[start_col].notna() & df[end_col].notna() & (df[start_col] != 0)

    if country:
        mask &= df['COUNTRY_NORM'] == _normalize(country)
    if metric:
        mask &= df['METRIC_NORM'] == _normalize(metric)
    if zone_type:
        mask &= df['ZONE_TYPE'].str.lower() == zone_type.lower()
    if zone_prioritization:
        mask &= df['ZONE_PRIORITIZATION'].str.lower() == zone_prioritization.lower()

    base = df[mask].copy()
    base['growth_abs'] = (base[end_col] - base[start_col]).round(4)
    base['growth_pct'] = (
        (base[end_col] - base[start_col]) / base[start_col].abs() * 100
    ).round(2)

    ascending = direction == "bottom"

    return (
        base
        .sort_values('growth_pct', ascending=ascending)
        [['COUNTRY', 'CITY', 'ZONE', 'METRIC', start_col, end_col, 'growth_abs', 'growth_pct']]
        .head(top_n)
        .reset_index(drop=True)
    )
