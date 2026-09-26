import io

import pandas as pd
import pytest

from src.ui.upload import handle_uploaded_file


def test_handle_uploaded_file_routes_csv_to_ingestion():
    text = "col_a,col_b\n1,2\n3,4\n"
    df, meta = handle_uploaded_file("dados.csv", text.encode("utf-8"))

    assert list(df["col_a"]) == [1, 3]
    assert meta["separator"] == ","


def _excel_bytes_with_sheets(sheets: dict[str, pd.DataFrame]) -> bytes:
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, sheet_name=name, index=False)
    return buffer.getvalue()


def test_handle_uploaded_file_defaults_to_first_sheet_when_none_given():
    file_bytes = _excel_bytes_with_sheets(
        {"Vendas": pd.DataFrame({"valor": [1, 2]}), "Clientes": pd.DataFrame({"nome": ["A"]})}
    )

    df, meta = handle_uploaded_file("planilha.xlsx", file_bytes)

    assert meta["sheet_name"] == "Vendas"
    assert list(df["valor"]) == [1, 2]


def test_handle_uploaded_file_uses_given_sheet_name():
    file_bytes = _excel_bytes_with_sheets(
        {"Vendas": pd.DataFrame({"valor": [1, 2]}), "Clientes": pd.DataFrame({"nome": ["A"]})}
    )

    df, meta = handle_uploaded_file("planilha.xlsx", file_bytes, sheet_name="Clientes")

    assert meta["sheet_name"] == "Clientes"
    assert list(df["nome"]) == ["A"]


def test_handle_uploaded_file_rejects_unsupported_extension():
    with pytest.raises(ValueError, match="não suportado"):
        handle_uploaded_file("dados.txt", b"qualquer coisa")
