import abc
from typing import Optional

from services.llm.models.llm_message import LlmMessage, LlmMessageRole
from services.llm.models.llm_reponse import LlmResponse


class LlmModel(abc.ABC):
    def __init__(self, model_name: str, is_vision_model: bool, system_role: str = "system", user_role: str = "user"):
        # userId -> arr
        self.model_name = model_name
        self.system_role = system_role
        self.user_role = user_role
        self.is_vision_model = is_vision_model

    @property
    @abc.abstractmethod
    def company_name(self) -> str:
        pass

    def generate_text(self, 
                      prompt: str, 
                      user_context: Optional[list[LlmMessage]]=None, 
                      img: Optional[str]=None, 
                      img_ext: Optional[str]="jpeg") -> LlmResponse:
        messages = [
            self._convert_to_llm_msg(msg) for msg in user_context
        ] if user_context else []
        
        messages.append(self._create_text_msg(self.user_role, prompt))
        
        if img and self.is_vision_model:
            # TODO make this shit less hardcoded
            messages[-1]["content"].append(self._create_img_msg(img, img_ext))

        response = self._make_llm_request(messages=messages)
        if not response.content:
            raise Exception(f"{self.company_name} returned empty str response for prompt: {prompt}, model: {self.model_name}.")
        
        return response

    @abc.abstractmethod   
    def _make_llm_request(self, messages: list[dict]) -> LlmResponse:
        pass

    def _convert_to_llm_msg(self, message: LlmMessage) -> dict:
        role = self.user_role if message.role == LlmMessageRole.USER else self.system_role
        return self._create_text_msg(role, message.content)
        
    def _create_text_msg(self, role: str, content: str) -> dict:
        return {
            "role": role, 
            "content": [
                {
                    "type": "text",
                    "text": content
                }
            ]
        }
    
    def _create_img_msg(self, img: Optional[str]=None, img_ext: Optional[str]="jpeg") -> dict:
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/{img_ext};base64,{img}",
                "detail": "low"
            }
        }