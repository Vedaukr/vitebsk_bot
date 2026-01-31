from datetime import datetime
import functools
import gc
from typing import Any, Callable, Iterable, Optional
from dataclasses import dataclass
import cachetools
from dateutil import parser
from bs4 import BeautifulSoup, ResultSet
from urllib.request import quote
from utils.md_utils import escape_markdown, get_md_link
from utils.filter_utils import filter_unique
from urllib.parse import urlparse, parse_qs
import pytz
import requests
import logging
import abc
import funcy as fy

DATA_STREAM_ATTR = "data-stream-"
MAX_GAMES = 10

MAX_CACHE_SIZE = 10
CACHE_TTL = 60*60 # 1 hour

PRAGUE_TZ = pytz.timezone("Europe/Prague")
KYIV_TZ = pytz.timezone("Europe/Kiev")

TZ_MAPPING = {
  "EEST": "UTC+3",
  "CEST": "UTC+2",
  "EDT": "UTC-4",
  "PET": "UTC-5",
  "BST": "UTC+1",
  "SGT": "UTC+8",
  "CST": "UTC+8",
  "AST": "UTC-4",
  "PDT": "UTC-7",
  "BRT": "UTC-3",
  "AEST": "UTC+10",
  "ART": "UTC-3",
}

logger = logging.getLogger(__name__)

@dataclass
class GameInfo:
    team1: str
    team2: str
    tournament: str
    tournament_link: str
    team1_liqlink: Optional[str] = None
    team2_liqlink: Optional[str] = None
    versus: Optional[str] = None
    start_time: Optional[datetime] = None
    stream_links: Optional[dict[str, list[str]]] = None

    def to_md_string(self) -> str:
        result = ""
        result += f"{get_md_link(self.tournament, self.tournament_link)}\n"

        versus = self.versus if self.versus else '-'
        team1 = get_md_link(self.team1, self.team1_liqlink) if self.team1_liqlink else escape_markdown(self.team1)
        team2 = get_md_link(self.team2, self.team2_liqlink) if self.team2_liqlink else escape_markdown(self.team2)
        result += f"{team1} {escape_markdown(versus)} {team2}\n"
        
        if self.start_time:
            pg_nowtime = datetime.now().astimezone(PRAGUE_TZ)
            pg_time = self.start_time.astimezone(PRAGUE_TZ)
            kyiv_time = self.start_time.astimezone(KYIV_TZ)
            
            diff_mins = round((pg_time - pg_nowtime).total_seconds()/60)
            if diff_mins > 60:
                time_str = f"{pg_time.strftime('%d %b %Y')} | {pg_time.strftime('%H:%M')} European | {kyiv_time.strftime('%H:%M')} Kyiv"
            elif diff_mins > 0:
                time_str = f"In {diff_mins} mins"
            else:
                time_str = "Already started"

            result += f"{escape_markdown(time_str)}\n"
        
        if self.stream_links:
            for (stream_type, stream_links) in self.stream_links.items():
                for stream_link in stream_links:
                    result += f"{get_md_link(stream_type.capitalize(), stream_link)}\n"

        result += "\n"
        return result

class LiquipediaService:
    def __init__(self, appname, api_route):
        __metaclass__ = abc.ABCMeta
        self.games_cache = cachetools.TTLCache(maxsize=MAX_CACHE_SIZE, ttl=CACHE_TTL)
        self.appname = appname
        self.__headers = {'User-Agent': appname, 'Accept-Encoding': 'gzip'}
        self.base_url = 'https://liquipedia.net'
        self.base_api_url = f'{self.base_url}{api_route}'

    @property
    @abc.abstractmethod
    def sport_name(self) -> str:
        pass
    
    @property
    @abc.abstractmethod
    def tournament_selector(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def match_details_selector(self) -> str:
        pass

    @abc.abstractmethod
    def _get_matches(self) -> ResultSet[Any]:
        pass

    # Todo: refactor 
    def parse(self,page):
        success, soup = False, None

        url = f"{self.base_api_url}action=parse&format=json&page={page}"
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

    def get_upcoming_and_ongoing_games(self, filters:list[Callable[[GameInfo], bool]]=None, max_games=MAX_GAMES, update_stream_links=True) -> list[GameInfo]:
        if not (games := self.games_cache.get(self.sport_name)):
            games = []
            matches = self._get_matches()
            
            if not matches:
                logger.warning("No matches were found in liquipedia service.")
            
            for match in matches:
                try:
                    game = {}

                    team_left = match.find(class_='match-info-header-opponent-left')
                    game['team1'] = team_left.get_text().strip()
                    tl_liq_link = team_left.find('a')
                    if tl_liq_link:
                        game['team1_liqlink'] = f"{self.base_url}{tl_liq_link.get('href')}"

                    team_right = match.find_all(class_='match-info-header-opponent')[1]
                    game['team2'] = team_right.get_text().strip()
                    tr_liq_link = team_right.find('a')
                    if tr_liq_link:
                        game['team2_liqlink'] = f"{self.base_url}{tr_liq_link.get('href')}"	
                    
                    versus_block = match.find(class_='match-info-header-scoreholder')
                    if versus_block:
                        game['versus'] = versus_block.get_text().strip()
                    
                    tournament_div = match.find(class_='match-info-tournament')
                    game['tournament'] = tournament_div.get_text().strip()
                    game['tournament_link'] = f"{self.base_url}{tournament_div.find('a').get('href')}"

                    try:
                        start_time_span = match.find(class_="timer-object")
                        if start_time_span:
                            data_timestamp = start_time_span.attrs.get('data-timestamp')
                            if data_timestamp:
                                game['start_time'] = datetime.fromtimestamp(int(data_timestamp))
                            else:
                                game['start_time'] = parser.parse(start_time_span.get_text(), tzinfos=TZ_MAPPING)
                    except AttributeError as atr_ex:
                        logger.error(f"Attribute error in LiquipediaService: {atr_ex}")
                    
                    
                    match_links = match.find(class_="match-info-links")
                    game['stream_links'] = self.get_stream_links(match_links)
                    game_info = GameInfo(**game)
                    games.append(game_info)	
                
                except AttributeError as atr_ex:
                    logger.error(f"Attribute error in LiquipediaService: {atr_ex}")

            if games:
                self.games_cache[self.sport_name] = games

        games = filter_unique(games, lambda game: (game.team1, game.team2))
        if filters:
            games = list(fy.filter(fy.all_fn(*filters), games))
        
        games = games[:max_games]

        # Updating links after applying filter since this action requires lots of time-heavy external http calls
        if update_stream_links:
            self.update_stream_links(games)

        return games
    
    def get_stream_links(self, match_links) -> dict[str, str]:
        filler_links = match_links.find_all('a')
        stream_links_tags = [link for link in filler_links if 'Special:Stream' in link.get('href')]
        if stream_links_tags:
            stream_links: dict[str, list[str]] = {}
            for sl_tag in stream_links_tags:
                try:
                    #0    1               2            3               4
                    # /counterstrike/Special:Stream/twitch/CCT_Counter-Strike_3
                    # /dota2/Special:Stream/twitch/Relog_Media_EN2
                    stream_link = sl_tag.get('href')
                    parts = stream_link.split(r'/')
                    stream_type = parts[3]

                    if not stream_type in stream_links:
                        stream_links[stream_type] = []
                    
                    stream_links[stream_type].append(self.get_full_stream_link(stream_link))
                except:
                    continue
                
            return stream_links
    
    def get_full_stream_link(self, stream_link: str) -> str:
        return f"{self.base_url}{stream_link}"

    def update_stream_links(self, games: Iterable[GameInfo]):
        for game in games:
            if game.stream_links:
                for (stream_type, liq_links) in game.stream_links.items():
                    for index, liq_link in enumerate(liq_links):
                        try:
                            if stream_type.startswith("twitch"):
                                ssurl = self.try_get_stream_service_url(liq_link)
                                if ssurl:
                                    liq_links[index] = f"https://www.twitch.tv/{parse_qs(ssurl.query)['channel'][0]}"

                            elif stream_type.startswith("youtube"):
                                ssurl = self.try_get_stream_service_url(liq_link)
                                if ssurl:
                                    liq_links[index] = f"https://www.youtube.com/watch?v={ssurl.path.split('/')[-1]}"
                            
                            elif stream_type.startswith("kick"):
                                ssurl = self.try_get_stream_service_url(liq_link)
                                if ssurl:
                                    liq_links[index] = f"https://kick.com/{ssurl.path.split('/')[-1]}"

                        except Exception as e:
                            logger.error(f"Error occured while updating {liq_link}:\n{e}")
    
    @functools.lru_cache(maxsize=100, typed=False)
    def try_get_stream_service_url(self, url):
        response = requests.get(url, headers=self.__headers)
        if response.status_code == 200:
            liq_page = BeautifulSoup(response.content, features="lxml")
            stream_iframe = liq_page.find('iframe')
            if stream_iframe:
                return urlparse(stream_iframe.get('src'))


class CsService(LiquipediaService):
    def __init__(self, appname):
        super().__init__(appname, api_route="/counterstrike/api.php?")
    
    @property
    def sport_name(self) -> str:
        return "counterstrike"
    
    @property
    def tournament_selector(self) -> str:
         return 'text-nowrap'
    
    @property
    def match_details_selector(self) -> str:
        return 'match-filler'
    
    def _get_matches(self) -> ResultSet[Any]:
        soup, __ = self.parse('Liquipedia:Matches')
        return soup.find_all('div', class_='match-info')
        
    
class DotaService(LiquipediaService):
    def __init__(self, appname):
        super().__init__(appname, api_route="/dota2/api.php?")
    
    @property
    def sport_name(self) -> str:
        return "dota2"
    
    @property
    def tournament_selector(self) -> str:
        return 'match-tournament' 
    
    @property
    def match_details_selector(self) -> str:
        return 'match-details'
    
    def _get_matches(self) -> ResultSet[Any]:
        soup, __ = self.parse('Liquipedia:Upcoming_and_ongoing_matches')
        return soup.find_all('div', class_='match-info')
    
    
    
