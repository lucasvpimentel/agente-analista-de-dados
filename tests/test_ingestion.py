import io

import pandas as pd
import pytest

from src import config, ingestion


def test_load_csv_detects_semicolon_and_comma_decimal():
    text = "col_a;col_b\n1,5;2,5\n3,0;4,0\n"
    df, meta = ingestion.load_csv(text.encode("utf-8"))

    assert list(df["col_a"]) == [1.5, 3.0]
    assert meta["separator"] == ";"
    assert meta["decimal"] == ","
    assert meta["encoding"] == "utf-8"


def test_load_csv_detects_comma_separator():
    text = "col_a,col_b\n1.5,2.5\n3.0,4.0\n"
    df, meta = ingestion.load_csv(text.encode("utf-8"))

    assert list(df["col_a"]) == [1.5, 3.0]
    assert meta["separator"] == ","
    assert meta["decimal"] == "."


def test_load_csv_falls_back_to_latin1_encoding():
    text = "nome;valor\ncafé;10\n"
    df, meta = ingestion.load_csv(text.encode("latin-1"))

    assert df["nome"][0] == "café"
    assert meta["encoding"] == "latin-1"


def test_load_csv_rejects_file_above_size_limit(monkeypatch):
    monkeypatch.setattr(config, "MAX_FILE_SIZE_MB", 0.000001)
    text = "col_a,col_b\n1,2\n"

    with pytest.raises(ValueError, match="tamanho"):
        ingestion.load_csv(text.encode("utf-8"))


def test_load_csv_samples_when_above_row_limit(monkeypatch):
    monkeypatch.setattr(config, "MAX_ROWS_FULL_PROFILE", 5)
    rows = "\n".join(f"{i},{i * 2}" for i in range(10))
    text = f"col_a,col_b\n{rows}\n"

    df, meta = ingestion.load_csv(text.encode("utf-8"))

    assert len(df) == 5
    assert meta["sampled"] is True
    assert meta["original_rows"] == 10


def _excel_bytes_with_sheets(sheets: dict[str, pd.DataFrame]) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)
    return buffer.getvalue()


def test_list_excel_sheets_returns_all_sheet_names():
    file_bytes = _excel_bytes_with_sheets(
        {
            "Vendas": pd.DataFrame({"a": [1, 2]}),
            "Clientes": pd.DataFrame({"b": [3, 4]}),
        }
    )

    sheets = ingestion.list_excel_sheets(file_bytes)

    assert sheets == ["Vendas", "Clientes"]


def test_load_excel_reads_selected_sheet():
    file_bytes = _excel_bytes_with_sheets(
        {
            "Vendas": pd.DataFrame({"valor": [100, 200]}),
            "Clientes": pd.DataFrame({"nome": ["Ana", "Bia"]}),
        }
    )

    df, meta = ingestion.load_excel(file_bytes, sheet_name="Clientes")

    assert list(df["nome"]) == ["Ana", "Bia"]
    assert meta["sheet_name"] == "Clientes"
