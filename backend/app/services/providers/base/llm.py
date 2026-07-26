from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the provider name (e.g. openai, gemini)"""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the active model name"""

    @abstractmethod
    def generate_chat_response(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.2
    ) -> dict[str, Any]:
        """
        Generates a standard chat response.
        Returns a dict: {'content': str, 'prompt_tokens': int, 'completion_tokens': int, 'latency': float, 'model': str}
        """

    @abstractmethod
    def generate_json_response(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.0
    ) -> list[dict[str, Any]] | dict[str, Any]:
        """
        Generates a strictly formatted JSON response.
        """
