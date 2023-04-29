from utils.singleton import Singleton
import openai, os
from settings import OPENAI_ORGANIZATION, OPENAI_TOKEN

openai.organization = OPENAI_ORGANIZATION
openai.api_key = OPENAI_TOKEN

MAX_TOKENS = 500

class OpenAiService(metaclass=Singleton):
    def __init__(self):
        self.context = []

    def get_response(self, prompt):
        context = "; ".join(self.context)
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                # disable context for now as it is way ineffective
                # {"role": "system", "content": context},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
            max_tokens=MAX_TOKENS,
            frequency_penalty=0.4,
            presence_penalty=0.6
        )
        self.context.append(prompt)
        return response["choices"][0]["message"][ "content"]

    def clear_context(self):
        self.context = []
