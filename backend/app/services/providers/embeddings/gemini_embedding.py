import time
import requests
from typing import Tuple, List
from app.services.providers.base.embedding import BaseEmbeddingProvider
from app.ai_config import ai_config

class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self._active_model = None
        self._resolve_model()
        
    def _resolve_model(self):
        """Dynamically detect which embedding model is supported by this API key."""
        try:
            list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={self.api_key}"
            res = requests.get(list_url).json()
            available = []
            for m in res.get('models', []):
                if 'embedContent' in m.get('supportedGenerationMethods', []):
                    name = m['name'].replace("models/", "")
                    available.append(name)
                    
            # Check preferred order
            preferred_order = ["gemini-embedding-2", "text-embedding-004", "embedding-001"]
            for pref in preferred_order:
                if pref in available:
                    self._active_model = pref
                    # Sync to AI config
                    ai_config.embedding_model = self._active_model
                    return
                    
            # Fallback to the first available if none of the preferred matched
            if available:
                self._active_model = available[0]
                ai_config.embedding_model = self._active_model
            else:
                self._active_model = "embedding-001" # Safe fallback
        except Exception as e:
            print(f"Failed to resolve Gemini models: {e}. Falling back to default.")
            self._active_model = "gemini-embedding-2"

    @property
    def provider_name(self) -> str:
        return "gemini"
        
    @property
    def model_name(self) -> str:
        return self._active_model
        
    @property
    def dimension(self) -> int:
        return 768

    def get_embedding(self, text: str) -> Tuple[List[float], float]:
        if not text or not text.strip():
            raise ValueError("Cannot generate embedding for empty text")
            
        start_time = time.time()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self._active_model}:embedContent?key={self.api_key}"
        payload = {
            "model": f"models/{self._active_model}",
            "content": {
                "parts": [{"text": text}]
            },
            "outputDimensionality": self.dimension
        }
        
        try:
            res = requests.post(url, json=payload)
            if res.status_code != 200:
                raise Exception(f"Gemini API Error: {res.text}")
            
            data = res.json()
            embedding = data.get("embedding", {}).get("values", [])
            
            if not embedding or len(embedding) != self.dimension:
                # Never pad or truncate! Just validate.
                if len(embedding) != self.dimension:
                    raise Exception(f"Expected {self.dimension} dims, got {len(embedding)}")
                
            latency = time.time() - start_time
            return embedding, latency
            
        except Exception as e:
            raise Exception(f"Failed to generate Gemini embedding: {str(e)}")
