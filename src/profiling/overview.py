"""Visão geral do dataset: dimensões, memória, duplicatas e nulos."""

import pandas as pd


def compute_overview(df: pd.DataFrame) -> dict:
    total_cells = df.size
    pct_null_total = float(df.isna().sum().sum() / total_cells * 100) if total_cells else 0.0

    return {
        "n_rows": len(df),
        "n_columns": df.shape[1],
        "memory_usage_bytes": int(df.memory_usage(deep=True).sum()),
        "n_duplicate_rows": int(df.duplicated().sum()),
        "pct_null_total": pct_null_total,
    }
