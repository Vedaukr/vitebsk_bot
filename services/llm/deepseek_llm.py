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
    def company_name(self) -> str:
        return "Deepseek"
    
    def _make_llm_request(self, messages: list[dict]) -> LlmResponse:
        # TODO
        # The system message of deepseek-reasoner must be put on the beginning of the message sequence 
        if 'reasoner' in self.model_name:
            messages = [messages[-1]]
        
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            timeout=120
        )

        response_message = response.choices[0].message.content
        reasoning_content = ""
        if hasattr(response.choices[0].message, 'reasoning_content'):
            reasoning_content = response.choices[0].message.reasoning_content
        
        metadata = LlmMetadata(total_tokens=response.usage.total_tokens, reasoning=reasoning_content)
        return LlmResponse(content=response_message, metadata=metadata)
    
    def _create_text_msg(self, role: str, content: str) -> dict:
        return {
            "role": role, 
            "content": content
        }