import abc
from typing import Optional

from services.llm.models.llm_reponse import LlmResponse


class LlmModel(abc.ABC):
    def __init__(self, model_name: str, is_vision_model: bool):
        # userId -> arr
        self.model_name = model_name
        self.is_vision_model = is_vision_model

    @property
    @abc.abstractmethod
    def company_name() -> str:
        pass

    @abc.abstractmethod
    def generate_text(self, prompt:str, img:Optional[str]=None, img_ext:Optional[str]="jpeg") -> LlmResponse:
        # TODO add context msgs
        pass

