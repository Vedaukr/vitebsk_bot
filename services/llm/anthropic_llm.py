import copy
from typing import Optional
from services.llm.llm_model import LlmModel
from services.llm.models.llm_reponse import LlmMetadata, LlmResponse
from utils.singleton import Singleton
import anthropic

from settings import ANTHROPIC_API_KEY

default_settings = {
    "max_tokens": 2000,
    "temperature": 0.75
}

class AnthropicLlm(LlmModel):
    
    def __init__(self, model_name: str, is_vision_model: bool = True):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        super().__init__(model_name=model_name, is_vision_model=is_vision_model)

    @property
    def company_name() -> str:
        return "Anthropic"
    
    def generate_text(self, prompt:str, img:Optional[str]=None, img_ext:Optional[str]="jpeg") -> LlmResponse:
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]

        if img and self.is_vision_model:
            
            # wtf anthropic?
            if img_ext == 'jpg':
                img_ext = 'jpeg'
            
            messages[-1]["content"].append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": f"image/{img_ext}",
                    "data": img
                }
            })

        response = self.client.messages.create(
            model=self.model_name,
            max_tokens=default_settings["max_tokens"],
            temperature=default_settings["temperature"],
            #system=context_str,
            messages=messages
        )

        response_message = response.content[0].text
        if not response_message:
            raise Exception(f"Anthropic returned empty str response for prompt: {prompt}, model: {self.model_name}.")

        total_tokens = response.usage.input_tokens + response.usage.output_tokens
        metadata = LlmMetadata(total_tokens=total_tokens)
        return LlmResponse(content=response_message, metadata=metadata)