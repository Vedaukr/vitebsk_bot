from utils.singleton import Singleton
import requests

class TzService(metaclass=Singleton):
    def __init__(self):
        self.base_url = "http://api.geonames.org/timezoneJSON?"
        self.username = "vitebsk_bot"
        self.retry_count = 5

    def get_timezone(self, latitude, longitude) -> str:
        retry_count = self.retry_count
        while retry_count:
            try:
                response = requests.get(f"{self.base_url}lat={latitude}&lng={longitude}&username={self.username}").json()
                return response["timezoneId"]
            except Exception:
                retry_count -= 1
        return "Europe/London"   