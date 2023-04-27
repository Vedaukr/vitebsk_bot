from utils.singleton import Singleton
from settings import STABLE_HORDE_API_KEY

class ImageGenarationService(metaclass=Singleton):
    def __init__(self):
        self.context = []

    def get_response(self, prompt):
        payload = {
            "prompt": prompt,
            "params": {
                "height": 512,
                "width": 512,
            }
        }
        pass

