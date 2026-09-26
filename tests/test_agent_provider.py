import httpx
import openai

from src.agent.provider import OpenAIProvider


def _request() -> httpx.Request:
    return httpx.Request("GET", "https://api.openai.com/v1/models")


class _FakeModels:
    def __init__(self, error: Exception | None = None):
        self._error = error

    def list(self):
        if self._error:
            raise self._error
        return ["gpt-4o-mini"]


class _FakeClient:
    def __init__(self, error: Exception | None = None):
        self.models = _FakeModels(error)


def _provider_with_fake_client(monkeypatch, error: Exception | None = None) -> OpenAIProvider:
    provider = OpenAIProvider(api_key="fake-key", model="gpt-4o-mini")
    monkeypatch.setattr(provider, "_client", _FakeClient(error))
    return provider


def test_validate_key_returns_valida_when_call_succeeds(monkeypatch):
    provider = _provider_with_fake_client(monkeypatch)

    result = provider.validate_key()

    assert result.status == "valida"


def test_validate_key_returns_invalida_on_authentication_error(monkeypatch):
    response = httpx.Response(status_code=401, request=_request())
    error = openai.AuthenticationError("invalid api key", response=response, body=None)
    provider = _provider_with_fake_client(monkeypatch, error)

    result = provider.validate_key()

    assert result.status == "invalida"


def test_validate_key_returns_sem_creditos_on_insufficient_quota(monkeypatch):
    response = httpx.Response(status_code=429, request=_request())
    error = openai.RateLimitError(
        "insufficient quota", response=response, body={"code": "insufficient_quota"}
    )
    provider = _provider_with_fake_client(monkeypatch, error)

    result = provider.validate_key()

    assert result.status == "sem_creditos"


def test_validate_key_returns_erro_rede_on_connection_error(monkeypatch):
    error = openai.APIConnectionError(request=_request())
    provider = _provider_with_fake_client(monkeypatch, error)

    result = provider.validate_key()

    assert result.status == "erro_rede"


def test_provider_never_reads_streamlit_session_state():
    import inspect

    from src.agent import provider as provider_module

    source = inspect.getsource(provider_module)
    assert "st.session_state" not in source
    assert "import streamlit" not in source


def test_chat_yields_text_chunks_from_stream(monkeypatch):
    provider = OpenAIProvider(api_key="fake-key", model="gpt-4o-mini")

    class _Delta:
        def __init__(self, content):
            self.content = content

    class _Choice:
        def __init__(self, content):
            self.delta = _Delta(content)

    class _Chunk:
        def __init__(self, content):
            self.choices = [_Choice(content)]

    class _FakeCompletions:
        def create(self, **kwargs):
            assert kwargs["stream"] is True
            return iter([_Chunk("Olá"), _Chunk(" mundo"), _Chunk(None)])

    class _FakeChat:
        completions = _FakeCompletions()

    class _StreamingFakeClient:
        chat = _FakeChat()

    monkeypatch.setattr(provider, "_client", _StreamingFakeClient())

    chunks = list(provider.chat(messages=[{"role": "user", "content": "oi"}], profile={}))

    assert chunks == ["Olá", " mundo"]


def test_generate_summary_returns_response_text(monkeypatch):
    provider = OpenAIProvider(api_key="fake-key", model="gpt-4o-mini")

    class _Message:
        content = "Resumo gerado."

    class _Choice:
        message = _Message()

    class _Response:
        choices = [_Choice()]

    class _FakeCompletions:
        def create(self, **kwargs):
            assert kwargs.get("stream", False) is False
            return _Response()

    class _FakeChat:
        completions = _FakeCompletions()

    class _FakeClient:
        chat = _FakeChat()

    monkeypatch.setattr(provider, "_client", _FakeClient())

    summary = provider.generate_summary(profile={"overview": {"n_rows": 10}})

    assert summary == "Resumo gerado."
