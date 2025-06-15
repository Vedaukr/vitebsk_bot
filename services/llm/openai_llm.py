from typing import Optional
from services.llm.llm_model import LlmModel
from services.llm.models.llm_reponse import LlmMetadata, LlmResponse
from openai import NOT_GIVEN, ChatCompletion, OpenAI
from settings import settings

OPENAI_TOKEN = settings['OPENAI_TOKEN']
OPENAI_ORGANIZATION = settings['OPENAI_ORGANIZATION']

default_settings = {
    "max_tokens": 4000,
    "temperature": 0.75,
    "frequency_penalty": 0.4,
    "presence_penalty": 0.6,
}

class OpenAiLlm(LlmModel):
    
    def __init__(self, 
                 model_name: str, 
                 is_vision_model: bool = True, 
                 system_role: str = "system",
                 api_key: str = OPENAI_TOKEN,
                 organization: Optional[str] = OPENAI_ORGANIZATION,
                 base_url: Optional[str] = None):
        self.client = OpenAI(api_key=api_key, organization=organization, base_url=base_url)
        super().__init__(model_name, is_vision_model, system_role)
        
    @property
    def company_name(self) -> str:
        return "OpenAI"
    
    def _make_llm_request(self, messages: list[dict]) -> LlmResponse:
        response = self._make_request(messages=messages)
        response_message = response.choices[0].message.content
        metadata = LlmMetadata(total_tokens=response.usage.total_tokens)
        return LlmResponse(content=response_message, metadata=metadata)
    
    def _make_request(self, messages) -> ChatCompletion:
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=default_settings["temperature"],
            max_tokens=int(default_settings["max_tokens"]),
            frequency_penalty=default_settings["frequency_penalty"],
            presence_penalty=default_settings["presence_penalty"]
        )
    
# Openai O-series
class OpenAiOSeriesLlm(OpenAiLlm):

    def __init__(self, model_name: str, reasoning_effort: Optional[str] = None):
        
        # o1-mini/o1-preview models doesn't support reasoning_effort
        # but passing None doesn't work since None and NOT_GIVEN are *different* for openai
        # I hate openai API
        self.reasoning_effort = reasoning_effort or NOT_GIVEN
        
        super().__init__(model_name, is_vision_model=False, system_role="user")
    
    def _make_request(self, messages) -> ChatCompletion:
        return self.client.chat.completions.create(
            model=self.model_name,
            reasoning_effort=self.reasoning_effort,
            messages=messages,
            max_completion_tokens=int(default_settings["max_tokens"])
        )
    

# Grok via openai
class GrokLlm(OpenAiLlm):
    
    def _make_request(self, messages) -> ChatCompletion:
        return self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=default_settings["temperature"],
            max_tokens=int(default_settings["max_tokens"])
        )