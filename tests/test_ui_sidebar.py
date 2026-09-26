from src.ui.sidebar import STATUS_LABELS, clear_key_state, status_label


def test_clear_key_state_removes_all_agent_related_keys():
    session_state = {
        "openai_api_key": "sk-fake",
        "openai_model": "gpt-4o-mini",
        "key_validation_status": "valida",
        "key_validation_message": "Chave válida.",
        "chat_history": [{"role": "user", "content": "oi"}],
        "unrelated_key": "mantém",
    }

    clear_key_state(session_state)

    assert "openai_api_key" not in session_state
    assert "openai_model" not in session_state
    assert "key_validation_status" not in session_state
    assert "key_validation_message" not in session_state
    assert "chat_history" not in session_state
    assert session_state["unrelated_key"] == "mantém"


def test_clear_key_state_is_safe_on_empty_state():
    session_state: dict = {}

    clear_key_state(session_state)

    assert session_state == {}


def test_status_label_covers_all_known_statuses():
    for status in ("nao_configurada", "valida", "invalida", "sem_creditos", "erro_rede"):
        level, message = status_label(status)
        assert level in STATUS_LABELS_LEVELS
        assert isinstance(message, str) and message


STATUS_LABELS_LEVELS = {"info", "success", "error", "warning"}


def test_status_label_defaults_to_nao_configurada_for_unknown_status():
    level, message = status_label("algum_status_desconhecido")

    assert (level, message) == status_label("nao_configurada")


def test_status_label_never_includes_the_api_key():
    fake_key = "sk-super-secreta-123"
    for status in STATUS_LABELS:
        _, message = status_label(status)
        assert fake_key not in message
