from utils.singleton import Singleton
from openai import OpenAI
from settings import DEEPSEEK_API_KEY

class DeepseekService(metaclass=Singleton):
    def __init__(self):
        # userId -> arr
        self.client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com", max_retries=0)

    def generate_text(self, prompt, model_name="deepseek-reasoner"):
        messages = [
            {
                "role": "user", 
                "content": prompt
            }
        ]

        response = self.client.chat.completions.create(
            model=model_name,
            messages=messages,
            timeout=30
        )

        response_message = response.choices[0].message.content
        if not response_message:
            raise Exception(f"Deepseek service returned empty str response for prompt: {prompt}, model: {model_name}.")
        
        reasoning_content = ""
        if hasattr(response.choices[0].message, 'reasoning_content'):
            reasoning_content = response.choices[0].message.reasoning_content
        
        return response_message, reasoning_content
