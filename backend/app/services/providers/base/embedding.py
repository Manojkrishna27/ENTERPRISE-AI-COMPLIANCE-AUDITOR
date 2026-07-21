from abc import ABC, abstractmethod
from typing import Tuple, List

class BaseEmbeddingProvider(ABC):
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
        
    @property
    @abstractmethod
    def dimension(self) -> int:
        """Returns the dimension of the embedding vector"""
        pass

    @abstractmethod
    def get_embedding(self, text: str) -> Tuple[List[float], float]:
        """
        Generates an embedding vector for the given text.
        Returns a tuple of (vector, latency_in_seconds).
        """
        pass
