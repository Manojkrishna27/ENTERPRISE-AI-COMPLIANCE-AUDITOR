from abc import ABC, abstractmethod
from typing import Dict, Any, List, Union

class BaseLLMProvider(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key
        
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the provider name (e.g. openai, gemini)"""
        pass
        
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Returns the active model name"""
        pass

    @abstractmethod
    def generate_chat_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
        """
        Generates a standard chat response.
        Returns a dict: {'content': str, 'prompt_tokens': int, 'completion_tokens': int, 'latency': float, 'model': str}
        """
        pass

    @abstractmethod
    def generate_json_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Generates a strictly formatted JSON response.
        """
        pass
