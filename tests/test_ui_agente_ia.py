import httpx
import openai
import pandas as pd
import pytest

from src.profiling.pipeline import build_profile
from src.ui.tabs.agente_ia import generate_summary_safe


def _request() -> httpx.Request:
    return httpx.Request("GET", "https://api.openai.com/v1/chat/completions")


def _sample_profile_and_df():
    df = pd.DataFrame({"valor": [1, 2, 3, 4, 5]})
    return build_profile(df), df


class _FakeProvider:
    def __init__(self, error: Exception | None = None, summary: str = "Resumo gerado."):
        self._error = error
        self._summary = summary

    def generate_summary(self, context: dict) -> str:
        if self._error:
            raise self._error
        return self._summary


def test_generate_summary_safe_returns_summary_on_success():
    profile, df = _sample_profile_and_df()
    provider = _FakeProvider(summary="Dataset com 5 linhas, sem alertas relevantes.")

    summary, error = generate_summary_safe(provider, profile, df)

    assert summary == "Dataset com 5 linhas, sem alertas relevantes."
    assert error is None


def test_generate_summary_safe_handles_authentication_error():
    profile, df = _sample_profile_and_df()
    response = httpx.Response(status_code=401, request=_request())
    error = openai.AuthenticationError("invalid key", response=response, body=None)
    provider = _FakeProvider(error=error)

    summary, error_message = generate_summary_safe(provider, profile, df)

    assert summary is None
    assert "chave" in error_message.lower()


def test_generate_summary_safe_handles_rate_limit_error():
    profile, df = _sample_profile_and_df()
    response = httpx.Response(status_code=429, request=_request())
    error = openai.RateLimitError("quota exceeded", response=response, body=None)
    provider = _FakeProvider(error=error)

    _, error_message = generate_summary_safe(provider, profile, df)

    assert "cota" in error_message.lower() or "limite" in error_message.lower()


def test_generate_summary_safe_handles_timeout():
    profile, df = _sample_profile_and_df()
    error = openai.APITimeoutError(request=_request())
    provider = _FakeProvider(error=error)

    _, error_message = generate_summary_safe(provider, profile, df)

    assert "demorou" in error_message.lower() or "tempo" in error_message.lower()


def test_generate_summary_safe_handles_model_not_found():
    profile, df = _sample_profile_and_df()
    response = httpx.Response(status_code=404, request=_request())
    error = openai.NotFoundError("model not found", response=response, body=None)
    provider = _FakeProvider(error=error)

    _, error_message = generate_summary_safe(provider, profile, df)

    assert "modelo" in error_message.lower()


def test_generate_summary_safe_handles_connection_error():
    profile, df = _sample_profile_and_df()
    error = openai.APIConnectionError(request=_request())
    provider = _FakeProvider(error=error)

    _, error_message = generate_summary_safe(provider, profile, df)

    assert "conect" in error_message.lower() or "internet" in error_message.lower()


def test_generate_summary_safe_error_messages_never_leak_a_fake_key():
    profile, df = _sample_profile_and_df()
    fake_key = "sk-super-secreta-999"
    response = httpx.Response(status_code=401, request=_request())
    error = openai.AuthenticationError(f"invalid key {fake_key}", response=response, body=None)
    provider = _FakeProvider(error=error)

    _, error_message = generate_summary_safe(provider, profile, df)

    assert fake_key not in error_message


@pytest.mark.parametrize(
    "error_factory",
    [
        lambda: openai.AuthenticationError(
            "x", response=httpx.Response(status_code=401, request=_request()), body=None
        ),
        lambda: openai.RateLimitError(
            "x", response=httpx.Response(status_code=429, request=_request()), body=None
        ),
        lambda: openai.APITimeoutError(request=_request()),
        lambda: openai.NotFoundError(
            "x", response=httpx.Response(status_code=404, request=_request()), body=None
        ),
        lambda: openai.APIConnectionError(request=_request()),
    ],
)
def test_generate_summary_safe_always_returns_a_message_string(error_factory):
    profile, df = _sample_profile_and_df()
    provider = _FakeProvider(error=error_factory())

    summary, error_message = generate_summary_safe(provider, profile, df)

    assert summary is None
    assert isinstance(error_message, str) and error_message
