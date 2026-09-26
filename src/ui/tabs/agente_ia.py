"""Aba Agente IA: resumo executivo gerado pela LLM a partir do profile."""

import openai
import pandas as pd
import streamlit as st

from src import config
from src.agent.orchestrator import build_context
from src.agent.provider import OpenAIProvider


def generate_summary_safe(
    provider, profile: dict, sample_df: pd.DataFrame
) -> tuple[str | None, str | None]:
    """Chama o provider e traduz falhas em mensagens amigáveis, sem expor a chave."""
    context = build_context(profile, sample_df)
    try:
        return provider.generate_summary(context), None
    except openai.AuthenticationError:
        return None, "Chave inválida ou revogada. Configure uma chave válida na barra lateral."
    except openai.RateLimitError:
        return None, "Cota esgotada ou limite de uso atingido. Verifique seu plano na OpenAI."
    except openai.APITimeoutError:
        return None, "A OpenAI demorou demais para responder. Tente novamente."
    except openai.NotFoundError:
        return None, "Modelo indisponível para esta conta. Escolha outro modelo na barra lateral."
    except openai.APIConnectionError:
        return None, "Não foi possível conectar à OpenAI. Verifique sua internet."
    except openai.OpenAIError:
        return None, "Erro ao gerar o resumo executivo. Tente novamente."


def render(profile: dict, df: pd.DataFrame) -> None:
    api_key = st.session_state.get("openai_api_key")
    if not api_key:
        st.info("Configure sua chave da OpenAI na barra lateral para usar o Agente IA.")
        return

    model = st.session_state.get("openai_model", config.DEFAULT_MODEL)
    st.caption(
        "Dados enviados à OpenAI: profile resumido, schema das colunas e uma amostra "
        "pequena (nunca o dataset completo). O custo das chamadas é cobrado na conta "
        "dona da chave."
    )

    if st.button("Gerar resumo executivo"):
        provider = OpenAIProvider(api_key=api_key, model=model)
        with st.spinner("Gerando resumo..."):
            summary, error = generate_summary_safe(provider, profile, df)
        if error:
            st.error(error)
        else:
            st.session_state["executive_summary"] = summary

    if st.session_state.get("executive_summary"):
        st.markdown(st.session_state["executive_summary"])
