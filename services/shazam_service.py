import base64
from utils.singleton import Singleton
from settings import RAPID_API_SUBSCRIPTION_KEY
from dataclasses import dataclass
import requests, json

@dataclass
class ShazamResult:
    title: str
    singer: str
    #genre: str
    
class ShazamService(metaclass=Singleton):
    def __init__(self):
        self.base_url = 'https://shazam.p.rapidapi.com'
        self.headers = {
            "content-type": "text/plain",
            "X-RapidAPI-Key" : RAPID_API_SUBSCRIPTION_KEY,
            "X-RapidAPI-Host": "shazam.p.rapidapi.com"
        }

    def recognize_song(self, data: bytearray) -> ShazamResult:
        url = f"{self.base_url}/songs/detect"
        datastr = base64.b64encode(data)
        response = requests.post(url, data=datastr, headers=self.headers)
        response.raise_for_status()
        result_json = json.loads(response.text)
        
        if not "track" in result_json:
            return None
        
        return ShazamResult(title=result_json["track"]["title"], singer=result_json["track"]["subtitle"])

