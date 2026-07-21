import time
import json
from typing import Dict, Any, List, Union
from openai import OpenAI
from app.services.providers.base.llm import BaseLLMProvider
from app.ai_config import ai_config

class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.client = OpenAI(api_key=self.api_key)
        
    @property
    def provider_name(self) -> str:
        return "openai"
        
    @property
    def model_name(self) -> str:
        return ai_config.chat_model

    def generate_chat_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.2) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
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
                "model": self.model_name
            }
        except Exception as e:
            raise Exception(f"OpenAI LLM Generation failed: {str(e)}")

    def generate_json_response(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=temperature
            )
            content = response.choices[0].message.content
            data = json.loads(content)
            return data
        except Exception as e:
            raise Exception(f"OpenAI JSON Generation failed: {str(e)}")
