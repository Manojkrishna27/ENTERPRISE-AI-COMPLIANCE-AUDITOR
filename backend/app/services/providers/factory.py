from app.ai_config import ai_config
from app.services.providers.embeddings.openai_embedding import OpenAIEmbeddingProvider
from app.services.providers.embeddings.gemini_embedding import GeminiEmbeddingProvider
from app.services.providers.llms.openai_llm import OpenAILLMProvider
from app.services.providers.llms.gemini_llm import GeminiLLMProvider

def get_embedding_provider():
    if ai_config.provider == "gemini":
        return GeminiEmbeddingProvider(ai_config.api_key)
    else:
        return OpenAIEmbeddingProvider(ai_config.api_key)

def get_llm_provider():
    if ai_config.provider == "gemini":
        return GeminiLLMProvider(ai_config.api_key)
    else:
        return OpenAILLMProvider(ai_config.api_key)

embedding_provider = get_embedding_provider()
llm_provider = get_llm_provider()
