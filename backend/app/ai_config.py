import os


class AIConfig:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY", "").strip()

        # Determine provider based on key prefix
        if self.api_key and not self.api_key.startswith("sk-"):
            self.provider = "gemini"
            # Chat config
            self.chat_model = "gemini-1.5-flash"
            # Note: The embedding model will be dynamically resolved during initialization
            # to one of (gemini-embedding-2, text-embedding-004, embedding-001)
            self.embedding_model = "gemini-embedding-2"
            self.embedding_dimension = 768
        else:
            self.provider = "openai"
            self.chat_model = "gpt-4o"
            self.embedding_model = "text-embedding-3-small"
            self.embedding_dimension = 1536

    @property
    def contracts_collection(self):
        return f"contracts_{self.provider}_{self.embedding_dimension}"

    @property
    def policies_collection(self):
        return f"policies_{self.provider}_{self.embedding_dimension}"


ai_config = AIConfig()
