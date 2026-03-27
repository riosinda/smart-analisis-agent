import pandas as pd

ROLL_COLS = ['L8W_ROLL','L7W_ROLL','L6W_ROLL','L5W_ROLL','L4W_ROLL','L3W_ROLL','L2W_ROLL','L1W_ROLL','L0W_ROLL']

def get_zone_trend(df: pd.DataFrame, zone: str, metric: str, n_weeks: int = 8):
    weeks = ROLL_COLS[-(n_weeks + 1):]

    mask = (df['ZONE_NORM'] == zone) & (df['METRIC_NORM'] == metric)
    rows = df[mask]

    if rows.empty:
        return f"No se encontró zona '{zone}' con métrica '{metric}'"

    result = rows[['COUNTRY', 'CITY', 'ZONE'] + weeks].set_index(['COUNTRY', 'CITY', 'ZONE'])

    # Visualización
    """
    fig, ax = plt.subplots(figsize=(10, 4))
    for idx, row in result.iterrows():
        label = f"{idx[2]} ({idx[0]})"
        values = row.dropna()
        ax.plot(values.index, values.values, marker='o', label=label)

    ax.set_title(f'{metric} — Tendencia temporal')
    ax.set_xlabel('Semana')
    ax.set_ylabel('Valor')
    ax.legend()
    plt.tight_layout()
    plt.show()
    """

    return result.round(4)