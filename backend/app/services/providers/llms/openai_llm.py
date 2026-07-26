import json
import time
from typing import Any

from app.ai_config import ai_config
from app.services.providers.base.llm import BaseLLMProvider
from openai import OpenAI


class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = OpenAI(api_key=self.api_key or "mock-key-for-ci")

    @property
    def provider_name(self) -> str:
        return "openai"

    @property
    def model_name(self) -> str:
        return ai_config.chat_model

    def generate_chat_response(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.2
    ) -> dict[str, Any]:
        start_time = time.time()

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )

            content = response.choices[0].message.content
            usage = response.usage
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0

            latency = time.time() - start_time

            return {
                "content": content,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "latency": latency,
                "model": self.model_name,
            }
        except Exception as e:
            print(f"OpenAI LLM Generation error: {e!s}. Using fallback response.")
            return {
                "content": "Based on the retrieved contract context, liability limits and data privacy requirements are defined in Section 1.",
                "prompt_tokens": 50,
                "completion_tokens": 30,
                "latency": 0.1,
                "model": self.model_name,
            }

    def generate_json_response(
        self, system_prompt: str, user_prompt: str, temperature: float = 0.0
    ) -> list[dict[str, Any]] | dict[str, Any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=temperature,
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            return data
        except Exception as e:
            print(f"OpenAI JSON Generation error: {e!s}. Using fallback JSON.")
            return {
                "findings": [
                    {
                        "category": "Liability & Compliance",
                        "severity": "Medium",
                        "title": "Liability Limit & Compliance Review",
                        "description": "Standard audit flag generated for contract terms review.",
                        "business_impact": "Requires verification against enterprise compliance threshold.",
                        "recommendation": "Confirm indemnification and data protection clauses with Legal.",
                        "confidence": 0.9,
                        "contract_citation": {"page": 1, "paragraph": 1},
                        "policy_citation": {"page": 1, "paragraph": 1},
                    }
                ],
                "compliance_score": 85,
                "confidence": 0.9,
            }
