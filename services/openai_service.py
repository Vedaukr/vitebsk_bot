from utils.singleton import Singleton
from dataclasses import dataclass
import copy
import openai, os
from settings import OPENAI_ORGANIZATION, OPENAI_TOKEN

openai.organization = OPENAI_ORGANIZATION
openai.api_key = OPENAI_TOKEN

default_settings = {
    "max_tokens": 750,
    "temperature": 0.9,
    "frequency_penalty": 0.4,
    "presence_penalty": 0.6,
}

CONTEXT_SIZE = 5

class OpenAiService(metaclass=Singleton):
    def __init__(self):
        # userId -> arr
        self.context = {}
        self.params = copy.deepcopy(default_settings)

    def get_response(self, prompt, model_name="gpt-3.5-turbo", user_id="common"):
        context = self.get_or_create_context(user_id)
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": prompt},
            ],
            temperature=self.params["temperature"],
            max_tokens=self.params["max_tokens"],
            frequency_penalty=self.params["frequency_penalty"],
            presence_penalty=self.params["presence_penalty"]
        )
        self.context[user_id].append(prompt)
        return response["choices"][0]["message"]["content"]
    
    def reset_defaults(self):
        self.params = copy.deepcopy(default_settings)

    def get_or_create_context(self, user_id):
        if not user_id in self.context:
            self.context[user_id] = []
        
        context_arr = self.context[user_id]
        start = max(-CONTEXT_SIZE, -len(context_arr))
        return "; ".join(context_arr[start:])

    def clear_context(self, user_id="common"):
        self.context[user_id] = []
