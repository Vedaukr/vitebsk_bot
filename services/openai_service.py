from utils.singleton import Singleton
import openai, os
from settings import OPENAI_ORGANIZATION, OPENAI_TOKEN

openai.organization = OPENAI_ORGANIZATION
openai.api_key = OPENAI_TOKEN

MAX_TOKENS = 500
CONTEXT_SIZE = 5

class OpenAiService(metaclass=Singleton):
    def __init__(self):
        # userId -> arr
        self.context = {}

    def get_response(self, prompt, user_id="common"):
        context = self.get_or_create_context(user_id)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
            max_tokens=MAX_TOKENS,
            frequency_penalty=0.4,
            presence_penalty=0.6
        )
        self.context[user_id].append(prompt)
        return response["choices"][0]["message"]["content"]

    def get_or_create_context(self, user_id):
        if not user_id in self.context:
            self.context[user_id] = []
        
        context_arr = self.context[user_id]
        start = max(-CONTEXT_SIZE, -len(context_arr))
        return "; ".join(context_arr[start:])

    def clear_context(self, user_id="common"):
        self.context[user_id] = []
