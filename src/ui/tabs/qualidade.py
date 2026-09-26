"""Aba Qualidade: alertas priorizados e mapa de nulos."""

import plotly.express as px
import streamlit as st

from src.profiling.quality import null_percentages

_SEVERITY_ICON = {"alta": "🔴", "media": "🟡", "baixa": "🔵"}


def render(profile: dict, df) -> None:
    alerts = profile["quality_alerts"]
    if not alerts:
        st.success("Nenhum alerta de qualidade encontrado.")
    else:
        for alert in alerts:
            icon = _SEVERITY_ICON[alert["severity"]]
            column_label = f" (`{alert['column']}`)" if alert["column"] else ""
            st.write(f"{icon} {alert['issue']}{column_label}")

    st.subheader("Mapa de nulos por coluna")
    percentages = null_percentages(df)
    st.plotly_chart(
        px.bar(x=list(percentages.keys()), y=list(percentages.values()), title="% de nulos"),
        width='stretch',
    )
