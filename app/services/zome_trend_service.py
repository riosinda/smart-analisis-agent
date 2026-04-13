import pandas as pd
from typing import Any

ROLL_COLS = ['L8W_ROLL','L7W_ROLL','L6W_ROLL','L5W_ROLL','L4W_ROLL','L3W_ROLL','L2W_ROLL','L1W_ROLL','L0W_ROLL']

def get_zone_trend(df: pd.DataFrame,zone: str, metric: str, n_weeks: int = 8) -> dict[str, Any]:
    weeks = ROLL_COLS[-(n_weeks + 1):]

    mask = (
        df['ZONE'].str.contains(zone, case=False, na=False) & 
        (df['METRIC'] == metric)
    )
    rows = df[mask]

    # caso 1: zona/métrica no existe
    if rows.empty:
        return {
            "success": False,
            "data": None,
            "message": f"No se encontró zona '{zone}' con métrica '{metric}'."
        }

    # caso 2: zona existe pero sin datos en las semanas
    try:
        result = (
            rows[['COUNTRY', 'CITY', 'ZONE'] + weeks]
            .set_index(['COUNTRY', 'CITY', 'ZONE'])
            .round(4)
        )
    except KeyError as e:
        return {
            "success": False,
            "data": None,
            "message": f"Error al procesar columnas: {e}"
        }

    if result.isna().all(axis=None):
        return {
            "success": False,
            "data": None,
            "message": f"Zona '{zone}' encontrada pero sin datos en las últimas {n_weeks} semanas."
        }

    # caso 3: éxito
    return {
        "success": True,
        "data": result.reset_index().to_dict(orient="records"),
        "message": f"Se encontraron {len(result)} fila(s) para '{zone}'."
    }