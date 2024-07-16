from datetime import datetime
import functools
from typing import Any, Callable, Iterable, Optional
from dataclasses import dataclass
from dateutil import parser
from bs4 import BeautifulSoup, ResultSet
from urllib.request import quote
from utils.md_utils import escape_markdown, get_md_link
from utils.filter_utils import filter_unique
from urllib.parse import urlparse, parse_qs
import pytz
import requests
import abc
import funcy as fy

DATA_STREAM_ATTR = "data-stream-"
MAX_GAMES = 10

PRAGUE_TZ = pytz.timezone("Europe/Prague")
KYIV_TZ = pytz.timezone("Europe/Kiev")

TZ_MAPPING = {
  "EEST": "UTC+3",
  "CEST": "UTC+2",
  "EDT": "UTC-4",
  "PET": "UTC-5",
  "BST": "UTC+1",
  "SGT": "UTC+8",
  "CST": "UTC-6",
  "AST": "UTC-4",
  "PDT": "UTC-7",
  "BRT": "UTC-3",
  "AEST": "UTC+10",
  "ART": "UTC-3",
}

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
    stream_links: Optional[dict[str, str]] = None

    def to_md_string(self) -> str:
        result = ""
        result += f"{get_md_link(self.tournament, self.tournament_link)}\n"

        versus = self.versus if self.versus else '-'
        team1 = get_md_link(self.team1, self.team1_liqlink) if self.team1_liqlink else self.team1
        team2 = get_md_link(self.team2, self.team2_liqlink) if self.team2_liqlink else self.team2
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
            for (stream_type, stream_link) in self.stream_links.items():
                result += f"{get_md_link(stream_type.capitalize(), stream_link)}\n"

        result += "\n"
        return result

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
        games = []
        matches = self._get_matches()
        for match in matches:
            try:
                game = {}

                team_left = match.find('td', class_='team-left')
                game['team1'] = team_left.get_text().strip()
                tl_liq_link = team_left.find('a')
                if tl_liq_link:
                    game['team1_liqlink'] = f"{self.base_url}{tl_liq_link.get('href')}"

                team_right = match.find('td', class_='team-right')
                game['team2'] = team_right.get_text().strip()
                tr_liq_link = team_right.find('a')
                if tr_liq_link:
                    game['team2_liqlink'] = f"{self.base_url}{tr_liq_link.get('href')}"	
                
                versus_block = match.find('td', class_='versus')
                if versus_block:
                    game['versus'] = versus_block.get_text().strip()
                
                match_filler = 	match.find('td', class_='match-filler')
                tournament_div = match_filler.find('div', class_=self._get_tournament_selector())
                game['tournament'] = tournament_div.get_text().strip()
                game['tournament_link'] = f"{self.base_url}{tournament_div.find('a').get('href')}"

                try:
                    start_time = match_filler.find('span', class_="timer-object").get_text()
                    if start_time:
                        game['start_time'] = parser.parse(start_time, tzinfos=TZ_MAPPING)
                except Exception:
                    pass
                
                game['stream_links'] = self.get_stream_links(match_filler)
                game_info = GameInfo(**game)
                games.append(game_info)	
            
            except AttributeError:
                continue		
        
        games = filter_unique(games, lambda game: (game.team1, game.team2))
        if filters:
            games = list(fy.filter(fy.all_fn(*filters), games))
        
        games = games[:max_games]

        # Updating links after applying filter since this action requires lots of time-heavy external http calls
        if update_stream_links:
            self.update_stream_links(games)

        return games
    
    def get_stream_links(self, match_filler) -> dict[str, str]:
        streams_span = match_filler.find_all(lambda tag: any(attr.startswith(DATA_STREAM_ATTR) for attr in tag.attrs))
        if streams_span:
            stream_links = {}
            for attr in streams_span[0].attrs:
                if attr.startswith(DATA_STREAM_ATTR):
                    stream_type = attr[len(DATA_STREAM_ATTR):]
                    channel_name = streams_span[0].get(attr)
                    stream_links[stream_type] = self.get_stream(channel_name, stream_type)
            return stream_links
    
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
            stream_iframe = liq_page.find('iframe')
            if stream_iframe:
                return urlparse(stream_iframe.get('src'))


class CsService(LiquipediaService):
    def __init__(self, appname):
        super().__init__(appname, api_route="/counterstrike/api.php?")
    
    @property
    def sport_name(self) -> str:
        return "counterstrike"
    
    def get_stream_links(self, match_filler) -> dict[str, str]:
        filler_links = match_filler.find_all('a')
        stream_links_tags = [link for link in filler_links if 'Special:Stream' in link.get('href')]
        if stream_links_tags:
            stream_links = {}
            for sl_tag in stream_links_tags:
                try:
                    #0    1               2            3               4
                    # /counterstrike/Special:Stream/twitch/CCT_Counter-Strike_3
                    parts = sl_tag.get('href').split(r'/')
                    stream_type, channel_name = parts[3], parts[4]
                    stream_links[stream_type] = self.get_stream(channel_name, stream_type)
                except:
                    continue
                
            return stream_links
    
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
    
