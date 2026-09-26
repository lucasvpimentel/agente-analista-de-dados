"""Inferência de tipo por coluna: numérica, categórica, data, texto livre, booleana, id."""

import warnings

import pandas as pd

from src import config


def _cardinality_ratio(series: pd.Series) -> float:
    return series.nunique() / len(series)


def _infer_object_column_type(series: pd.Series) -> str:
    ratio = _cardinality_ratio(series)

    if ratio >= config.ID_CARDINALITY_RATIO:
        avg_length = series.astype(str).str.len().mean()
        if avg_length > config.FREE_TEXT_MIN_AVG_LENGTH:
            return "texto_livre"
        return "id"

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        parsed_dates = pd.to_datetime(series, errors="coerce")
    if parsed_dates.notna().mean() >= config.DATE_PARSE_THRESHOLD:
        return "data"

    if ratio <= config.CATEGORICAL_MAX_UNIQUE_RATIO:
        return "categorica"

    return "texto_livre"


def infer_column_type(series: pd.Series) -> str:
    non_null = series.dropna()
    if non_null.empty:
        return "texto_livre"

    if pd.api.types.is_bool_dtype(series):
        return "booleana"
    if pd.api.types.is_datetime64_any_dtype(series):
        return "data"
    if pd.api.types.is_numeric_dtype(series):
        return "numerica"

    return _infer_object_column_type(non_null)


def infer_types(df: pd.DataFrame, overrides: dict[str, str] | None = None) -> dict[str, str]:
    overrides = overrides or {}
    return {
        column: overrides.get(column, infer_column_type(df[column])) for column in df.columns
    }
