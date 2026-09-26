"""Estatísticas de colunas data/hora: intervalo, granularidade, lacunas, série por período."""

import pandas as pd

_FREQ_BY_GRANULARITY = {"horaria": "h", "diaria": "D", "mensal": "MS", "anual": "YS"}
_PERIOD_BY_GRANULARITY = {"horaria": "h", "diaria": "D", "mensal": "M", "anual": "Y"}


def detect_granularity(series: pd.Series) -> str:
    unique_sorted = series.dropna().sort_values().unique()
    diffs = pd.Series(unique_sorted).diff().dropna()
    if diffs.empty:
        return "diaria"

    median_diff = diffs.median()
    if median_diff <= pd.Timedelta(hours=1):
        return "horaria"
    if median_diff <= pd.Timedelta(days=2):
        return "diaria"
    if median_diff <= pd.Timedelta(days=35):
        return "mensal"
    return "anual"


def detect_gaps(series: pd.Series) -> list[pd.Timestamp]:
    non_null = series.dropna()
    if non_null.empty:
        return []

    granularity = detect_granularity(non_null)
    freq = _FREQ_BY_GRANULARITY[granularity]
    full_range = pd.date_range(non_null.min(), non_null.max(), freq=freq)
    actual = pd.DatetimeIndex(non_null.unique())
    return full_range.difference(actual).tolist()


def count_by_period(series: pd.Series) -> dict:
    non_null = series.dropna()
    if non_null.empty:
        return {}

    granularity = detect_granularity(non_null)
    freq = _PERIOD_BY_GRANULARITY[granularity]
    counts = non_null.dt.to_period(freq).value_counts().sort_index()
    return {str(period): int(count) for period, count in counts.items()}


def compute_datetime_stats(series: pd.Series) -> dict:
    non_null = series.dropna()

    return {
        "min": non_null.min(),
        "max": non_null.max(),
        "granularity": detect_granularity(non_null),
        "gaps": detect_gaps(non_null),
        "counts_by_period": count_by_period(non_null),
    }
