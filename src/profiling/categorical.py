"""Estatísticas descritivas para colunas categóricas: cardinalidade, moda, top N, raras."""

import pandas as pd

from src import config

TOP_N = 10


def compute_categorical_stats(series: pd.Series) -> dict:
    non_null = series.dropna()
    value_counts = non_null.value_counts()

    return {
        "cardinality": int(non_null.nunique()),
        "mode": value_counts.index[0] if not value_counts.empty else None,
        "top_frequencies": value_counts.head(TOP_N).to_dict(),
    }


def detect_rare_categories(series: pd.Series) -> list[str]:
    non_null = series.dropna()
    frequencies = non_null.value_counts(normalize=True)
    return frequencies[frequencies < config.RARE_CATEGORY_THRESHOLD].index.tolist()
