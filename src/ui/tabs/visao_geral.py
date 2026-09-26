"""Aba Visão Geral: métricas gerais do dataset."""

import streamlit as st


def render(profile: dict) -> None:
    overview = profile["overview"]

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Linhas", overview["n_rows"])
    col2.metric("Colunas", overview["n_columns"])
    col3.metric("Linhas duplicadas", overview["n_duplicate_rows"])
    col4.metric("% nulos (total)", f"{overview['pct_null_total']:.1f}%")

    st.caption(f"Uso de memória: {overview['memory_usage_bytes'] / 1_000_000:.2f} MB")

    st.subheader("Tipos de coluna detectados")
    st.dataframe(
        [{"coluna": col, "tipo": tipo} for col, tipo in profile["types"].items()],
        hide_index=True,
    )
