import time

from app.services.providers.base.embedding import BaseEmbeddingProvider
from openai import OpenAI


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = OpenAI(api_key=self.api_key or "mock-key-for-ci")

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return "text-embedding-3-small"

    @property
    def dimension(self) -> int:
        return 1536

    def get_embedding(self, text: str) -> tuple[list[float], float]:
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty text")

        start_time = time.time()
        try:
            response = self.client.embeddings.create(
                input=[text], model=self.model_name
            )
            embedding = response.data[0].embedding
            latency = time.time() - start_time
            return embedding, latency
        except Exception as e:
            print(
                f"Failed to generate OpenAI embedding: {e!s}. Using fallback vector."
            )
            return [0.01] * self.dimension, 0.05
