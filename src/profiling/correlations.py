"""Correlações Pearson/Spearman (numéricas) e Cramér's V (categóricas)."""

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency

from src import config


def compute_correlation_matrices(df: pd.DataFrame) -> dict:
    numeric_df = df.select_dtypes(include="number")
    truncated = numeric_df.shape[1] > config.MAX_CORRELATION_COLUMNS
    if truncated:
        numeric_df = numeric_df.iloc[:, : config.MAX_CORRELATION_COLUMNS]

    return {
        "pearson": numeric_df.corr(method="pearson"),
        "spearman": numeric_df.corr(method="spearman"),
        "truncated": truncated,
    }


def find_high_correlation_pairs(
    corr_matrix: pd.DataFrame, threshold: float | None = None
) -> list[dict]:
    threshold = config.CORRELATION_THRESHOLD if threshold is None else threshold
    columns = corr_matrix.columns
    pairs = []

    for i in range(len(columns)):
        for j in range(i + 1, len(columns)):
            value = corr_matrix.iloc[i, j]
            if abs(value) >= threshold:
                pairs.append(
                    {"col_a": columns[i], "col_b": columns[j], "correlation": float(value)}
                )

    pairs.sort(key=lambda pair: -abs(pair["correlation"]))
    return pairs


def cramers_v(series_a: pd.Series, series_b: pd.Series) -> float:
    contingency = pd.crosstab(series_a, series_b)
    chi2 = chi2_contingency(contingency)[0]
    n = contingency.sum().sum()
    r, k = contingency.shape

    phi2_corrected = max(0.0, chi2 / n - ((k - 1) * (r - 1)) / (n - 1))
    r_corrected = r - ((r - 1) ** 2) / (n - 1)
    k_corrected = k - ((k - 1) ** 2) / (n - 1)
    denominator = min(k_corrected - 1, r_corrected - 1)

    if denominator <= 0:
        return 0.0
    return float(np.sqrt(phi2_corrected / denominator))
