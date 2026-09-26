"""Qualidade de dados: nulos, colunas constantes/quase-únicas, duplicatas e alertas."""

import pandas as pd

from src import config

_SEVERITY_RANK = {"alta": 0, "media": 1, "baixa": 2}


def null_percentages(df: pd.DataFrame) -> dict[str, float]:
    return {column: float(df[column].isna().mean() * 100) for column in df.columns}


def constant_columns(df: pd.DataFrame) -> list[str]:
    return [column for column in df.columns if df[column].dropna().nunique() == 1]


def near_unique_columns(df: pd.DataFrame) -> list[str]:
    result = []
    for column in df.columns:
        non_null = df[column].dropna()
        if len(non_null) == 0:
            continue
        if non_null.nunique() / len(non_null) >= config.ID_CARDINALITY_RATIO:
            result.append(column)
    return result


def duplicate_row_count(df: pd.DataFrame) -> int:
    return int(df.duplicated().sum())


def generate_alerts(df: pd.DataFrame) -> list[dict]:
    alerts = []

    for column, pct_null in null_percentages(df).items():
        if pct_null == 100.0:
            alerts.append(
                {"column": column, "issue": "coluna totalmente nula", "severity": "alta"}
            )

    for column in constant_columns(df):
        alerts.append({"column": column, "issue": "coluna constante", "severity": "media"})

    for column in near_unique_columns(df):
        alerts.append(
            {
                "column": column,
                "issue": "coluna quase-única (possível identificador)",
                "severity": "baixa",
            }
        )

    if duplicate_row_count(df) > 0:
        alerts.append(
            {"column": None, "issue": "linhas duplicadas no dataset", "severity": "media"}
        )

    alerts.sort(key=lambda alert: _SEVERITY_RANK[alert["severity"]])
    return alerts
