import os
import sys
from dotenv import load_dotenv

# Load from project root .env
load_dotenv("/home/mk/Documents/AICompliance&ContractAuditor/.env")

# Add backend to path
sys.path.append("/home/mk/Documents/AICompliance&ContractAuditor/backend")

from app.services.providers.embedding_provider import embedding_provider
from app.services.providers.llm_provider import llm_provider

print("=== Testing Embedding Provider ===")
try:
    emb, lat = embedding_provider.get_embedding("Test question")
    print(f"Success! Vector length: {len(emb)}, Latency: {lat}s")
except Exception as e:
    print(f"Embedding Provider Failed: {e}")

print("\n=== Testing LLM Provider ===")
try:
    res = llm_provider.generate_chat_response("You are a helpful bot.", "Hello")
    print(f"Success! Response: {res['content']}, Latency: {res['latency']}s")
except Exception as e:
    print(f"LLM Provider Failed: {e}")
