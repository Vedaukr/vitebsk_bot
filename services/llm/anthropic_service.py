import copy
import cachetools
from utils.singleton import Singleton
from dataclasses import dataclass
import anthropic

from settings import ANTHROPIC_API_KEY

CONTEXT_SIZE = 5
MAX_CACHE_SIZE = 50
CACHE_TTL = 30 * 60 # 30 minutes

default_settings = {
    "max_tokens": 2000,
    "temperature": 0.75,
    "frequency_penalty": 0.4,
    "presence_penalty": 0.6,
}

class AnthropicService(metaclass=Singleton):
    def __init__(self):
        # userId -> arr
        self.context = cachetools.TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL)
        self.params = copy.deepcopy(default_settings)
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    
    def generate_text(self, prompt, model_name="claude-3-5-haiku-latest", user_id="common", base64_image=None, img_ext="jpeg"):
        context = self.get_or_create_context(user_id)
        context_str = self.convert_context_to_str(context)
        messages=[
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

        if base64_image:
            messages[0]["content"].append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": f"image/{img_ext}",
                    "data": base64_image
                }
            })

        message = self.client.messages.create(
            model=model_name,
            max_tokens=default_settings["max_tokens"],
            temperature=default_settings["temperature"],
            system=context_str,
            messages=messages
        )

        return message.content[0].text
    
    # todo move thos to some base LLM service class
    def reset_defaults(self):
        self.params = copy.deepcopy(default_settings)

    def get_or_create_context(self, user_id) -> list[str]:
        if not user_id in self.context:
            self.context[user_id] = []
        
        return self.context[user_id]
    
    def convert_context_to_str(self, context: list[str]) -> str:
        start = max(-CONTEXT_SIZE, -len(context))
        return "; ".join(context[start:])

    def clear_context(self, user_id="common"):
        if user_id in self.context:
            del self.context[user_id]