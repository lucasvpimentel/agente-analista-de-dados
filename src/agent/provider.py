"""Interface do provedor de LLM e implementação para a OpenAI."""

from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass

import openai
from openai import OpenAI


@dataclass
class ValidationResult:
    status: str  # "valida" | "invalida" | "sem_creditos" | "erro_rede"
    message: str


class LLMProvider(ABC):
    @abstractmethod
    def validate_key(self) -> ValidationResult: ...

    @abstractmethod
    def generate_summary(self, profile: dict) -> str: ...

    @abstractmethod
    def chat(self, messages: list[dict], profile: dict) -> Iterator[str]: ...


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self._client = OpenAI(api_key=api_key)
        self._model = model

    def validate_key(self) -> ValidationResult:
        try:
            self._client.models.list()
            return ValidationResult("valida", "Chave válida.")
        except openai.AuthenticationError:
            return ValidationResult("invalida", "Chave inválida.")
        except openai.RateLimitError:
            return ValidationResult(
                "sem_creditos", "Limite de uso atingido ou sem créditos disponíveis."
            )
        except openai.APIConnectionError:
            return ValidationResult("erro_rede", "Não foi possível conectar à OpenAI.")
        except openai.OpenAIError:
            return ValidationResult("erro_rede", "Erro ao validar a chave junto à OpenAI.")

    def generate_summary(self, profile: dict) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "user",
                    "content": f"Gere um resumo executivo em português deste profile de "
                    f"dados: {profile}",
                }
            ],
        )
        return response.choices[0].message.content

    def chat(self, messages: list[dict], profile: dict) -> Iterator[str]:
        system_message = {
            "role": "system",
            "content": f"Contexto do dataset (profile resumido): {profile}",
        }
        stream = self._client.chat.completions.create(
            model=self._model,
            messages=[system_message, *messages],
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
