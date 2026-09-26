"""Sidebar de configuração do Agente IA: chave da API, modelo e validação."""

import streamlit as st

from src import config
from src.agent.provider import OpenAIProvider

_KEY_RELATED_STATE_KEYS = (
    "openai_api_key",
    "openai_model",
    "key_validation_status",
    "key_validation_message",
    "chat_history",
)

STATUS_LABELS = {
    "nao_configurada": ("info", "Configure sua chave da OpenAI para usar o Agente IA."),
    "valida": ("success", "Chave válida."),
    "invalida": ("error", "Chave inválida. Verifique e tente novamente."),
    "sem_creditos": ("warning", "Chave sem créditos ou limite de uso atingido."),
    "erro_rede": ("error", "Não foi possível validar a chave (erro de rede)."),
}


def status_label(status: str) -> tuple[str, str]:
    return STATUS_LABELS.get(status, STATUS_LABELS["nao_configurada"])


def clear_key_state(session_state) -> None:
    for key in _KEY_RELATED_STATE_KEYS:
        session_state.pop(key, None)


def render() -> None:
    st.sidebar.subheader("Configuração do Agente IA")

    api_key_input = st.sidebar.text_input("Chave da API OpenAI", type="password")
    model = st.sidebar.selectbox(
        "Modelo", config.MODELS, index=config.MODELS.index(config.DEFAULT_MODEL)
    )

    validate_col, clear_col = st.sidebar.columns(2)

    if validate_col.button("Validar"):
        if not api_key_input:
            st.sidebar.error("Informe uma chave antes de validar.")
        else:
            result = OpenAIProvider(api_key=api_key_input, model=model).validate_key()
            st.session_state["key_validation_status"] = result.status
            st.session_state["key_validation_message"] = result.message
            st.session_state["openai_model"] = model
            if result.status == "valida":
                st.session_state["openai_api_key"] = api_key_input
            else:
                st.session_state.pop("openai_api_key", None)

    if clear_col.button("Limpar chave"):
        clear_key_state(st.session_state)

    status = st.session_state.get("key_validation_status", "nao_configurada")
    level, message = status_label(status)
    getattr(st.sidebar, level)(message)

    st.sidebar.caption("Sua chave é usada só durante esta sessão e não é armazenada.")
    st.sidebar.markdown("[Gerar uma chave na OpenAI](https://platform.openai.com/api-keys)")
