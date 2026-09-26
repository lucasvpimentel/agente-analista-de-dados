"""Monta o contexto (profile + schema + amostra) enviado ao LLM."""

import json

import numpy as np
import pandas as pd

from src import config

_OUTLIER_FIELDS = ("outliers_iqr", "outliers_zscore")


def _summarize_column(column_type: str, stats: dict) -> dict:
    if column_type == "numerica":
        summary = {key: value for key, value in stats.items() if key not in _OUTLIER_FIELDS}
        summary["outliers_iqr_count"] = stats["outliers_iqr"]["count"]
        summary["outliers_zscore_count"] = stats["outliers_zscore"]["count"]
        return summary
    if column_type == "data":
        summary = {key: value for key, value in stats.items() if key != "gaps"}
        summary["gaps_count"] = len(stats["gaps"])
        return summary
    return dict(stats)


def _clean_sample_value(value):
    if isinstance(value, float) and np.isnan(value):
        return None
    return value


def build_context(profile: dict, sample_df: pd.DataFrame) -> dict:
    raw_sample = sample_df.head(config.SAMPLE_ROWS_FOR_AGENT).to_dict(orient="records")
    sample = [
        {key: _clean_sample_value(value) for key, value in row.items()} for row in raw_sample
    ]
    columns = {
        column: _summarize_column(profile["types"][column], stats)
        for column, stats in profile["columns"].items()
    }

    return {
        "overview": profile["overview"],
        "schema": profile["types"],
        "columns": columns,
        "quality_alerts": profile["quality_alerts"],
        "high_correlation_pairs": profile["high_correlation_pairs"],
        "sample": sample,
    }


def _json_default(obj):
    if isinstance(obj, pd.Timestamp) or obj is pd.NaT:
        return obj.isoformat() if obj is not pd.NaT else None
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return None if np.isnan(obj) else float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    raise TypeError(f"Tipo não serializável em JSON: {type(obj)}")


def to_json_context(context: dict) -> str:
    return json.dumps(context, default=_json_default, ensure_ascii=False)
