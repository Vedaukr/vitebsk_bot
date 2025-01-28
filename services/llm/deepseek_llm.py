from typing import Optional
from services.llm.llm_model import LlmModel
from openai import OpenAI
from services.llm.models.llm_reponse import LlmMetadata, LlmResponse
from settings import DEEPSEEK_API_KEY

class DeepseekLlm(LlmModel):

    def __init__(self, model_name: str, is_vision_model: bool = False):
        # userId -> arr
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com", max_retries=0)
        super().__init__(model_name=model_name, is_vision_model=is_vision_model)

    @property
    def company_name() -> str:
        return "Deepseek"
    
    def generate_text(self, prompt:str, img:Optional[str]=None, img_ext:Optional[str]="jpeg") -> LlmResponse:
        messages = [
            {
                "role": "user", 
                "content": prompt
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            timeout=30
        )

        response_message = response.choices[0].message.content
        if not response_message:
            raise Exception(f"Deepseek service returned empty str response for prompt: {prompt}, model: {self.model_name}.")
        
        reasoning_content = ""
        if hasattr(response.choices[0].message, 'reasoning_content'):
            reasoning_content = response.choices[0].message.reasoning_content
        
        metadata = LlmMetadata(total_tokens=response.usage.total_tokens, reasoning=reasoning_content)
        return LlmResponse(content=response_message, metadata=metadata)
