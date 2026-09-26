"""Upload de planilha e preview na página principal."""

import pandas as pd
import streamlit as st

from src import ingestion


def handle_uploaded_file(
    filename: str, file_bytes: bytes, sheet_name: str | None = None
) -> tuple[pd.DataFrame, dict]:
    """Roteia o arquivo pro leitor certo (CSV ou Excel) e retorna dados + metadados."""
    lower_name = filename.lower()
    if lower_name.endswith(".csv"):
        return ingestion.load_csv(file_bytes)
    if lower_name.endswith(".xlsx"):
        if sheet_name is None:
            sheet_name = ingestion.list_excel_sheets(file_bytes)[0]
        return ingestion.load_excel(file_bytes, sheet_name)
    raise ValueError("Formato de arquivo não suportado. Envie um arquivo .csv ou .xlsx.")


def render() -> tuple[pd.DataFrame | None, dict | None]:
    """Renderiza o uploader, o seletor de aba (se aplicável) e o preview."""
    uploaded = st.file_uploader("Envie sua planilha", type=["csv", "xlsx"])
    if uploaded is None:
        return None, None

    file_bytes = uploaded.read()
    sheet_name = None
    if uploaded.name.lower().endswith(".xlsx"):
        sheets = ingestion.list_excel_sheets(file_bytes)
        sheet_name = st.selectbox("Escolha a aba", sheets) if len(sheets) > 1 else sheets[0]

    try:
        df, meta = handle_uploaded_file(uploaded.name, file_bytes, sheet_name)
    except ValueError as error:
        st.error(str(error))
        return None, None

    if meta.get("sampled"):
        st.warning(
            f"Dataset grande: mostrando amostra de {len(df)} de {meta['original_rows']} linhas."
        )
    st.dataframe(df.head())
    return df, meta
