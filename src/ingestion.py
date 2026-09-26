"""Leitura de CSV e Excel com detecção automática de formato (padrão BR)."""

import csv
import io

import pandas as pd

from src import config


def _check_size(file_bytes: bytes) -> None:
    size_mb = len(file_bytes) / 1_000_000
    if size_mb > config.MAX_FILE_SIZE_MB:
        raise ValueError(
            f"Arquivo excede o tamanho máximo permitido de {config.MAX_FILE_SIZE_MB}MB."
        )


def _decode(file_bytes: bytes) -> tuple[str, str]:
    for encoding in ("utf-8", "latin-1"):
        try:
            return file_bytes.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    raise ValueError("Não foi possível decodificar o arquivo (tentado UTF-8 e Latin-1).")


def _detect_separator(text: str) -> str:
    sample = text[:5000]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        return dialect.delimiter
    except csv.Error:
        return ","


def _sample_if_needed(df: pd.DataFrame) -> tuple[pd.DataFrame, bool, int]:
    original_rows = len(df)
    if original_rows > config.MAX_ROWS_FULL_PROFILE:
        sampled_df = df.sample(config.MAX_ROWS_FULL_PROFILE, random_state=0)
        return sampled_df, True, original_rows
    return df, False, original_rows


def load_csv(file_bytes: bytes) -> tuple[pd.DataFrame, dict]:
    _check_size(file_bytes)
    text, encoding = _decode(file_bytes)
    separator = _detect_separator(text)
    decimal = "," if separator == ";" else "."

    df = pd.read_csv(io.StringIO(text), sep=separator, decimal=decimal)
    df, sampled, original_rows = _sample_if_needed(df)

    metadata = {
        "encoding": encoding,
        "separator": separator,
        "decimal": decimal,
        "sampled": sampled,
        "original_rows": original_rows,
    }
    return df, metadata


def list_excel_sheets(file_bytes: bytes) -> list[str]:
    _check_size(file_bytes)
    return pd.ExcelFile(io.BytesIO(file_bytes)).sheet_names


def load_excel(file_bytes: bytes, sheet_name: str) -> tuple[pd.DataFrame, dict]:
    _check_size(file_bytes)
    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet_name)
    df, sampled, original_rows = _sample_if_needed(df)

    metadata = {
        "sheet_name": sheet_name,
        "sampled": sampled,
        "original_rows": original_rows,
    }
    return df, metadata
