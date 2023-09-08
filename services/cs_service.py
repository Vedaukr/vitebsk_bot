import requests
from bs4 import BeautifulSoup
from urllib.request import quote
from utils.singleton import Singleton

class CsService(metaclass=Singleton):
    def __init__(self, appname):
        self.appname = appname
        self.__headers = {'User-Agent': appname, 'Accept-Encoding': 'gzip'}
        self.base_url = 'https://liquipedia.net'
        self.__base_url = f'{self.base_url}/counterstrike/api.php?'

    def parse(self,page):
        success, soup = False, None

        url = self.__base_url+'action=parse&format=json&page='+page
        response = requests.get(url, headers=self.__headers)
        if response.status_code == 200:
            try:
                page_html = response.json()['parse']['text']['*']
            except KeyError:
                raise Exception(response.json(),response.status_code)	
        else:
            raise Exception(response.json(),response.status_code)

        soup = BeautifulSoup(page_html,features="lxml")

        redirect = soup.find('ul',class_="redirectText")
        if redirect is None:
            return soup,None
        else:
            redirect_value = soup.find('a').get_text()
            redirect_value = quote(redirect_value)
            soup,__ = self.parse(redirect_value)
            return soup,redirect_value
        
    def get_upcoming_and_ongoing_games(self):
        games = []
        soup,__ = self.parse('Liquipedia:Matches')
        matches = soup.find_all('table',class_='infobox_matches_content')
        for match in matches:
            game = {}
            cells = match.find_all('td')
            try:
                game['team1'] = cells[0].find('span',class_='team-template-text').find('a').get('title')			
                game['team2'] = cells[2].find('span',class_='team-template-text').find('a').get('title')
                game['start_time'] = cells[3].find('span',class_="timer-object").get_text()
                game['tournament'] = cells[3].find('div').get_text().rstrip()
                game['tournament_link'] = f"{self.base_url}{cells[3].find('div').find('a').get('href')}"
                
                try:
                    twitch_channel = cells[3].find('span',class_="timer-object").get('data-stream-twitch')
                    if twitch_channel:
                        game['twitch_channel'] = self.get_stream(twitch_channel, "twitch")
                except AttributeError:
                    pass

                try:
                    yt_channel = cells[3].find('span',class_="timer-object").get('data-stream-youtube')
                    if yt_channel:
                        game['youtube_channel'] = self.get_stream(yt_channel, "youtube")
                except AttributeError:
                    pass

                games.append(game)	
            
            except AttributeError:
                continue		
                    
        return games
    
    def get_stream(self, stream_id: str, stream_type: str) -> str:
        return f"{self.base_url}/counterstrike/Special:Stream/{stream_type}/{stream_id}"
    