"""Aba Correlações: heatmap Pearson/Spearman e pares de alta correlação."""

import plotly.express as px
import streamlit as st


def render(profile: dict) -> None:
    correlations = profile["correlations"]

    if correlations["pearson"].empty:
        st.info("Nenhuma coluna numérica disponível para calcular correlações.")
        return

    if correlations["truncated"]:
        st.warning("Muitas colunas numéricas: matriz de correlação truncada.")

    method = st.radio("Método", ["pearson", "spearman"], horizontal=True)
    st.plotly_chart(
        px.imshow(correlations[method], text_auto=".2f", title=f"Correlação ({method})"),
        width='stretch',
    )

    pairs = profile["high_correlation_pairs"]
    if pairs:
        st.subheader("Pares com correlação forte")
        st.dataframe(pairs, hide_index=True)
    else:
        st.caption("Nenhum par acima do limiar de correlação configurado.")
