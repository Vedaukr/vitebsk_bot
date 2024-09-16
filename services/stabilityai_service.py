from utils.singleton import Singleton
from dataclasses import dataclass
from settings import STABILITYAI_TOKEN
import requests
import base64

CONTENT_FILTERED = "CONTENT_FILTERED"

class StabilityAiService(metaclass=Singleton):
    def __init__(self):
        self.base_url = "https://api.stability.ai"

    def generate_image_beta(self, prompt: str, engine_id: str = "core") -> bytes:
        response = requests.post(
            f"{self.base_url}/v2beta/stable-image/generate/{engine_id}",
            headers={
                "authorization": f"Bearer {STABILITYAI_TOKEN}",
                "accept": "image/*"
            },
            files={"none": ''},
            data={
                "prompt": prompt,
                "output_format": "jpeg",
            },
        )
        response.raise_for_status()
        return response.content
    
    
    def generate_image(self, prompt: str, engine_id: str = "stable-diffusion-xl-1024-v1-0") -> bytes:
        response = requests.post(
            f"{self.base_url}/v1/generation/{engine_id}/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {STABILITYAI_TOKEN}"
            },
            json={
                "text_prompts": [
                    {
                        "text": prompt
                    }
                ],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30,
            },
        )
        response.raise_for_status()
        
        data = response.json()
        artifact = data["artifacts"][0]
        return base64.b64decode(artifact["base64"])
