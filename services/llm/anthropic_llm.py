import copy
from typing import Optional
from services.llm.llm_model import LlmModel
from services.llm.models.llm_reponse import LlmMetadata, LlmResponse
import anthropic

from settings import settings

ANTHROPIC_API_KEY = settings['ANTHROPIC_API_KEY']

default_settings = {
    "max_tokens": 4000,
    "temperature": 0.75
}

class AnthropicLlm(LlmModel):
    
    def __init__(self, model_name: str, is_vision_model: bool = True):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        system_role="assistant"
        super().__init__(model_name=model_name, is_vision_model=is_vision_model, system_role=system_role)

    @property
    def company_name(self) -> str:
        return "Anthropic"

    def _make_llm_request(self, messages: list[dict]) -> LlmResponse:
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=default_settings["max_tokens"],
            temperature=default_settings["temperature"],
            messages=messages
        )
        response_message = response.content[0].text
        total_tokens = response.usage.input_tokens + response.usage.output_tokens
        metadata = LlmMetadata(total_tokens=total_tokens)
        return LlmResponse(content=response_message, metadata=metadata)
    
    def _create_img_msg(self, role: str, img: Optional[str]=None, img_ext: Optional[str]="jpeg") -> dict:
        
        if img_ext == 'jpg':
            img_ext = 'jpeg'
        
        return {
            "role": role, 
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": f"image/{img_ext}",
                        "data": img
                    }
                }
            ]
        }
    

# Updated version for thinking-supporting models
class AnthropicThinkingLlm(AnthropicLlm):
    
    def __init__(self, model_name: str, is_vision_model: bool = True, thinking_budget: int = 2000):
        self.thinking_budget = thinking_budget
        super().__init__(model_name=model_name, is_vision_model=is_vision_model)

    def _make_llm_request(self, messages: list[dict]) -> LlmResponse:
        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=default_settings["max_tokens"],
            messages=messages,
            thinking={
                "type": "enabled",
                "budget_tokens": self.thinking_budget
            },
        )

        thinking_message = response.content[0].thinking
        response_message = response.content[1].text
        
        total_tokens = response.usage.input_tokens + response.usage.output_tokens
        metadata = LlmMetadata(total_tokens=total_tokens, reasoning=thinking_message)
        
        return LlmResponse(content=response_message, metadata=metadata)