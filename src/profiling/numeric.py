"""Estatísticas descritivas e detecção de outliers para colunas numéricas."""

import pandas as pd

from src import config


def compute_numeric_stats(series: pd.Series) -> dict:
    non_null = series.dropna()
    q1 = non_null.quantile(0.25)
    q3 = non_null.quantile(0.75)

    return {
        "mean": float(non_null.mean()),
        "median": float(non_null.median()),
        "std": float(non_null.std()),
        "min": float(non_null.min()),
        "max": float(non_null.max()),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(q3 - q1),
        "skewness": float(non_null.skew()),
        "kurtosis": float(non_null.kurt()),
        "n_zeros": int((non_null == 0).sum()),
        "n_negatives": int((non_null < 0).sum()),
    }


def detect_outliers_iqr(series: pd.Series) -> dict:
    non_null = series.dropna()
    q1 = non_null.quantile(0.25)
    q3 = non_null.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - config.OUTLIER_IQR_MULTIPLIER * iqr
    upper_bound = q3 + config.OUTLIER_IQR_MULTIPLIER * iqr

    outliers = non_null[(non_null < lower_bound) | (non_null > upper_bound)]
    return {"count": int(len(outliers)), "indices": outliers.index.tolist()}


def detect_outliers_zscore(series: pd.Series) -> dict:
    non_null = series.dropna()
    std = non_null.std()
    if std == 0:
        return {"count": 0, "indices": []}

    z_scores = (non_null - non_null.mean()) / std
    outliers = non_null[z_scores.abs() > config.OUTLIER_ZSCORE_THRESHOLD]
    return {"count": int(len(outliers)), "indices": outliers.index.tolist()}
