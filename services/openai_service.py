from utils.singleton import Singleton
from dataclasses import dataclass
import copy
import openai
import cachetools
from settings import OPENAI_ORGANIZATION, OPENAI_TOKEN

openai.organization = OPENAI_ORGANIZATION
openai.api_key = OPENAI_TOKEN

default_settings = {
    "max_tokens": 1000,
    "temperature": 0.9,
    "frequency_penalty": 0.4,
    "presence_penalty": 0.6,
}

CONTEXT_SIZE = 5
MAX_CACHE_SIZE = 50
CACHE_TTL = 30 * 60 # 30 minutes

class OpenAiService(metaclass=Singleton):
    def __init__(self):
        # userId -> arr
        self.context = cachetools.TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL)
        self.params = copy.deepcopy(default_settings)

    def generate_text(self, prompt, model_name="gpt-3.5-turbo", user_id="common", base64_image=None, img_ext="jpeg"):
        context = self.get_or_create_context(user_id)
        context_str = self.convert_context_to_str(context)
        messages = [
            {
                "role": "system", 
                "content": [
                    {
                        "type": "text",
                        "text": context_str
                    }
                ]
            },
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            },
        ]
        
        if base64_image:
            messages[1]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{img_ext};base64,{base64_image}",
                    "detail": "low"
                }
            })

        response = openai.ChatCompletion.create(
            model=model_name,
            messages=messages,
            temperature=self.params["temperature"],
            max_tokens=int(self.params["max_tokens"]),
            frequency_penalty=self.params["frequency_penalty"],
            presence_penalty=self.params["presence_penalty"]
        )

        context.append(prompt)
        return response["choices"][0]["message"]["content"]
    
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
