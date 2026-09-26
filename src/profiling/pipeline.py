"""Monta o profile completo do dataset combinando todas as análises de profiling."""

import pandas as pd

from src.profiling.categorical import compute_categorical_stats, detect_rare_categories
from src.profiling.correlations import compute_correlation_matrices, find_high_correlation_pairs
from src.profiling.datetime_stats import compute_datetime_stats
from src.profiling.numeric import compute_numeric_stats, detect_outliers_iqr, detect_outliers_zscore
from src.profiling.overview import compute_overview
from src.profiling.quality import generate_alerts
from src.profiling.types import infer_types


def _build_column_profile(series: pd.Series, column_type: str) -> dict:
    if column_type == "numerica":
        return {
            "type": column_type,
            **compute_numeric_stats(series),
            "outliers_iqr": detect_outliers_iqr(series),
            "outliers_zscore": detect_outliers_zscore(series),
        }
    if column_type == "categorica":
        return {
            "type": column_type,
            **compute_categorical_stats(series),
            "rare_categories": detect_rare_categories(series),
        }
    if column_type == "data":
        if not pd.api.types.is_datetime64_any_dtype(series):
            series = pd.to_datetime(series, errors="coerce")
        return {"type": column_type, **compute_datetime_stats(series)}
    return {"type": column_type}


def build_profile(df: pd.DataFrame, overrides: dict[str, str] | None = None) -> dict:
    types = infer_types(df, overrides)
    columns = {
        column: _build_column_profile(df[column], column_type)
        for column, column_type in types.items()
    }
    correlations = compute_correlation_matrices(df)

    return {
        "overview": compute_overview(df),
        "types": types,
        "columns": columns,
        "quality_alerts": generate_alerts(df),
        "correlations": correlations,
        "high_correlation_pairs": find_high_correlation_pairs(correlations["pearson"]),
    }
