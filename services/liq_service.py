from datetime import datetime
import functools
from typing import Any, Callable, Iterable, Optional
from dataclasses import dataclass
from dateutil import parser
from bs4 import BeautifulSoup, ResultSet
from urllib.request import quote
from utils.filter_utils import filter_unique
from urllib.parse import urlparse, parse_qs
import requests
import abc
import funcy as fy

DATA_STREAM_ATTR = "data-stream-"
MAX_GAMES = 10

@dataclass
class GameInfo:
    team1: str
    team2: str
    tournament: str
    tournament_link: str
    start_time: Optional[datetime] = None
    stream_links: Optional[dict[str, str]] = None

class LiquipediaService:
    def __init__(self, appname, api_route):
        __metaclass__ = abc.ABCMeta
        self.appname = appname
        self.__headers = {'User-Agent': appname, 'Accept-Encoding': 'gzip'}
        self.base_url = 'https://liquipedia.net'
        self.base_api_url = f'{self.base_url}{api_route}'

    @property
    @abc.abstractmethod
    def sport_name(self) -> str:
        pass

    @abc.abstractmethod
    def _get_matches(self) -> ResultSet[Any]:
        pass
    
    @abc.abstractmethod
    def _get_tournament_selector(self) -> str:
        pass

    # Todo: refactor 
    def parse(self,page):
        success, soup = False, None

        url = self.base_api_url+'action=parse&format=json&page='+page
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

    def get_upcoming_and_ongoing_games(self, filters:list[Callable[[GameInfo], bool]]=None, max_games=MAX_GAMES) -> list[GameInfo]:
        games = []
        matches = self._get_matches()
        for match in matches:
            try:
                game = {}
                game['team1'] = match.find('td', class_='team-left').get_text().strip()		
                game['team2'] = match.find('td', class_='team-right').get_text().strip()
                
                match_filler = 	match.find('td', class_='match-filler')
                tournament_div = match_filler.find('div', class_=self._get_tournament_selector())
                game['tournament'] = tournament_div.get_text().strip()
                game['tournament_link'] = f"{self.base_url}{tournament_div.find('a').get('href')}"

                try:
                    start_time = match_filler.find('span', class_="timer-object").get_text()
                    if start_time:
                        game['start_time'] = parser.parse(start_time)
                except Exception:
                    pass
                
                streams_span = match_filler.find_all(lambda tag: any(attr.startswith(DATA_STREAM_ATTR) for attr in tag.attrs))
                if streams_span:
                    stream_links = game['stream_links'] = {}
                    for attr in streams_span[0].attrs:
                        if attr.startswith(DATA_STREAM_ATTR):
                            stream_type = attr[len(DATA_STREAM_ATTR):]
                            channel_name = streams_span[0].get(attr)
                            stream_links[stream_type] = self.get_stream(channel_name, stream_type)
                
                game_info = GameInfo(**game)
                games.append(game_info)	
            
            except AttributeError:
                continue		
        
        games = filter_unique(games, lambda game: (game.team1, game.team2))
        if filters:
            games = list(fy.filter(fy.all_fn(*filters), games))

        # Updating links after applying filter since this action requires lots of time-heavy external http calls
        games = games[:max_games]
        self.update_stream_links(games)

        return games
    
    def get_stream(self, stream_id: str, stream_type: str) -> str:
        # Workaround for cases like Twitch2
        if str.isnumeric(stream_type[-1]):
            stream_type = stream_type[:-1]
        
        return f"{self.base_url}/{self.sport_name}/Special:Stream/{stream_type}/{stream_id}"

    def update_stream_links(self, games: Iterable[GameInfo]):
        for game in games:
            if game.stream_links:
                for (stream_type, liq_link) in game.stream_links.items():
                    try:
                        if stream_type.startswith("twitch"):
                            ssurl = self.try_get_stream_service_url(liq_link)
                            if ssurl:
                                game.stream_links[stream_type] = f"https://www.twitch.tv/{parse_qs(ssurl.query)['channel'][0]}"

                        elif stream_type.startswith("youtube"):
                            ssurl = self.try_get_stream_service_url(liq_link)
                            if ssurl:
                                game.stream_links[stream_type] = f"https://www.youtube.com/watch?v={ssurl.path.split('/')[-1]}"
                        
                        elif stream_type.startswith("kick"):
                            ssurl = self.try_get_stream_service_url(liq_link)
                            if ssurl:
                                game.stream_links[stream_type] = f"https://kick.com/{ssurl.path.split('/')[-1]}"

                    except Exception:
                        pass
    
    @functools.lru_cache(maxsize=100, typed=False)
    def try_get_stream_service_url(self, url):
        response = requests.get(url, headers=self.__headers)
        if response.status_code == 200:
            liq_page = BeautifulSoup(response.content, features="lxml")
            return urlparse(liq_page.find('iframe').get('src'))


class CsService(LiquipediaService):
    def __init__(self, appname):
        super().__init__(appname, api_route="/counterstrike/api.php?")
    
    @property
    def sport_name(self) -> str:
        return "counterstrike"
    
    def _get_matches(self) -> ResultSet[Any]:
        soup, __ = self.parse('Liquipedia:Matches')
        return soup.find_all('table', class_='infobox_matches_content')
    
    def _get_tournament_selector(self) -> str:
        # I hate Liquipedia
        return 'text-nowrap'
        
    
class DotaService(LiquipediaService):
    def __init__(self, appname):
        super().__init__(appname, api_route="/dota2/api.php?")
    
    @property
    def sport_name(self) -> str:
        return "dota2"
    
    def _get_matches(self) -> ResultSet[Any]:
        soup, __ = self.parse('Liquipedia:Upcoming_and_ongoing_matches')
        return soup.find_all('table', class_='infobox_matches_content')
    
    def _get_tournament_selector(self) -> str:
        return 'tournament-text'
    
