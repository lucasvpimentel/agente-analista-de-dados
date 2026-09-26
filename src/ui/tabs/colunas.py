"""Aba Colunas: estatísticas detalhadas por coluna, com gráfico conforme o tipo."""

import pandas as pd
import plotly.express as px
import streamlit as st


def _render_numeric(series: pd.Series, stats: dict) -> None:
    metrics = st.columns(4)
    metrics[0].metric("Média", f"{stats['mean']:.2f}")
    metrics[1].metric("Mediana", f"{stats['median']:.2f}")
    metrics[2].metric("Desvio padrão", f"{stats['std']:.2f}")
    metrics[3].metric("Outliers (IQR)", stats["outliers_iqr"]["count"])

    st.plotly_chart(px.histogram(series, title="Histograma"), use_container_width=True)
    st.plotly_chart(px.box(series, title="Boxplot"), use_container_width=True)


def _render_categorical(stats: dict) -> None:
    st.metric("Cardinalidade", stats["cardinality"])
    if stats["rare_categories"]:
        st.warning(f"Categorias raras: {', '.join(map(str, stats['rare_categories']))}")

    frequencies = stats["top_frequencies"]
    st.plotly_chart(
        px.bar(x=list(frequencies.keys()), y=list(frequencies.values()), title="Top categorias"),
        use_container_width=True,
    )


def _render_datetime(stats: dict) -> None:
    st.metric("Granularidade", stats["granularity"])
    st.metric("Lacunas detectadas", len(stats["gaps"]))
    if stats["counts_by_period"]:
        st.plotly_chart(
            px.bar(
                x=list(stats["counts_by_period"].keys()),
                y=list(stats["counts_by_period"].values()),
                title="Contagem por período",
            ),
            use_container_width=True,
        )


def render(df: pd.DataFrame, profile: dict) -> None:
    column = st.selectbox("Escolha a coluna", df.columns)
    column_profile = profile["columns"][column]
    column_type = column_profile["type"]
    st.caption(f"Tipo detectado: {column_type}")

    if column_type == "numerica":
        _render_numeric(df[column], column_profile)
    elif column_type == "categorica":
        _render_categorical(column_profile)
    elif column_type == "data":
        _render_datetime(column_profile)
    else:
        st.info("Sem estatísticas específicas para este tipo de coluna.")
