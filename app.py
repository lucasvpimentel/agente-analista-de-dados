import pandas as pd
import streamlit as st

from src.profiling.pipeline import build_profile
from src.ui import sidebar, upload
from src.ui.tabs import colunas, correlacoes, qualidade, visao_geral


@st.cache_data
def _cached_profile(df: pd.DataFrame) -> dict:
    return build_profile(df)


st.set_page_config(page_title="DataLens", page_icon="📊", layout="wide")
st.title("DataLens — Agente IA Analista de Dados")
st.caption("Faça upload de uma planilha para começar.")

sidebar.render()

df, meta = upload.render()

if df is not None:
    profile = _cached_profile(df)
    tab_visao_geral, tab_colunas, tab_qualidade, tab_correlacoes = st.tabs(
        ["Visão Geral", "Colunas", "Qualidade", "Correlações"]
    )
    with tab_visao_geral:
        visao_geral.render(profile)
    with tab_colunas:
        colunas.render(df, profile)
    with tab_qualidade:
        qualidade.render(profile, df)
    with tab_correlacoes:
        correlacoes.render(profile)
