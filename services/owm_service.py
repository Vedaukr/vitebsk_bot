from utils.singleton import Singleton
from pyowm.owm import OWM
from settings import OPENWEATHER_API_KEY
from pyowm.weatherapi25 import forecaster, observation

class OwmService(metaclass=Singleton):
    def __init__(self):
        self.wmanager = OWM(OPENWEATHER_API_KEY).weather_manager()

    def get_weather_at_place(self, city) -> observation.Observation:
        return self.wmanager.weather_at_place(city)
    
    def get_weather_forecast(self, city) -> forecaster.Forecaster:
        return self.wmanager.forecast_at_place(city, '3h')