from utils.singleton import Singleton
import requests
import re
import numpy as np

class SearchService(metaclass=Singleton):
    def __init__(self):
        self.base_url = 'https://duckduckgo.com/'
        self.headers = {
            'dnt': '1',
            'x-requested-with': 'XMLHttpRequest',
            'accept-language': 'en-GB,en-US;q=0.8,en;q=0.6,ms;q=0.4',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'referer': 'https://duckduckgo.com/',
            'authority': 'duckduckgo.com',
        }

    def get_image(self, keywords):
        params = {
            'q': keywords
        }
        res = requests.post(self.base_url, data=params)
        searchObj = re.search(r'vqd=([\d-]+)\&', res.text, re.M | re.I)

        if not searchObj:
            raise Exception("Token Parsing Failed !")
        
        params = (
            ('l', 'wt-wt'),
            ('o', 'json'),
            ('q', keywords),
            ('vqd', searchObj.group(1)),
            ('f', ',,,'),
            ('p', '2')
        )

        requestUrl = f"{self.base_url}/i.js"
        res = requests.get(requestUrl, headers=self.headers, params=params)

        if not res.ok:
            raise Exception(res.status_code)
        
        data = res.json()
        obj = np.random.choice(data["results"])
        return obj['image']


    # def get_image(self, obj):
    #     img_link = obj['image']
    #     return requests.get(img_link).content

