from utils.singleton import Singleton
from settings import BING_SUBSCRIPTION_KEY
import requests
import numpy as np
from googlesearch import search

class SearchService(metaclass=Singleton):
    def __init__(self):
        self.base_url = 'https://api.bing.microsoft.com/v7.0/images/search'
        self.headers = {
            "Ocp-Apim-Subscription-Key" : BING_SUBSCRIPTION_KEY
        }

    def get_image(self, keywords):
        params = {
            'q': keywords,
            "license": "public", 
            "imageType": "photo",
            "safeSearch": "Off"
        }
        response = requests.get(self.base_url, headers=self.headers, params=params)
        response.raise_for_status()
        search_results = response.json()
        return np.random.choice(search_results["value"])["contentUrl"]
    
    def get_search_results(self, search_prompt, site, res_count=5):
        query = f"{search_prompt}"
        if site:
            query = f"{query} site: {site}"
        return search(query, num=res_count, stop=res_count, pause=1)

