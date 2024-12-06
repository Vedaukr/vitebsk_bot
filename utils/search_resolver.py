from abc import ABC, abstractmethod
from utils.singleton import Singleton
from utils.md_utils import escape_markdown
import requests, re, logging

logger = logging.getLogger(__name__)

class SiteSearchHandler(ABC):
    def __init__(self) -> None:
        self.headers = {
            'Authorization': 'authorization',
            'cookie': 'hl=en'
        }
        self.cookies = {'CONSENT': 'YES+1'}

    @abstractmethod
    def get_triggers(self) -> tuple[str]:
        pass

    @abstractmethod
    def get_site_uri(self) -> str:
        pass

    def get_response(self, links: list[str]) -> str:
        message = "Results:\n"
        for count,link in enumerate(links):
            header = self.get_link_header(link)
            if not header:
                header = "Untitled"
            message += f"{count + 1}\. [{escape_markdown(header)}]({escape_markdown(link)})\n"
        return message
    
    def get_link_header(self, link: str) -> str:
        header = self.try_get_header_from_html(link)
        return header or link.split('/')[-1]
    
    def try_get_header_from_html(self, link: str) -> str:
        try:
            response = requests.get(link, timeout=5, headers=self.headers, cookies=self.cookies)
            response.raise_for_status()
            pattern = r"<title>(.*?)</title>"
            match = re.search(pattern, response.text)
            if match:
                return match.group(1)
        except Exception as e:
            logger.error(f"Error while trying to get header from link {link}:\n{e}.")

class SearchResolver(metaclass=Singleton):
    def __init__(self) -> None:
        self.handlers = []

    def register_handler(self, handler: SiteSearchHandler):
        self.handlers.append(handler)

    def get_site_search_handler(self, prompt: str) -> SiteSearchHandler:
        prompt = prompt.split(" ")[0]
        for handler in self.handlers:
            if prompt.lower() in handler.get_triggers():
                return handler

    
class StackOverflowHandler(SiteSearchHandler):
    def get_triggers(self) -> tuple[str]:
        return ("so", "stackoverflow", "стак", "со")
    
    def get_site_uri(self) -> str:
        return "stackoverflow.com"
    
    def get_link_header(self, link: str) -> str:
        header = link.split('/')[-1].split('-')
        return " ".join(header)
    
class StackExchangeHandler(SiteSearchHandler):
    def get_triggers(self) -> tuple[str]:
        return ("stex", "stackexchange", "стакэкс", "сэ")
    
    def get_site_uri(self) -> str:
        return "stackexchange.com"
    
    def get_link_header(self, link: str) -> str:
        header = link.split('/')[-1].split('-')
        return " ".join(header)
    
class RedditHandler(SiteSearchHandler):
    def get_triggers(self) -> tuple[str]:
        return ("red", "reddit", "ред", "реддит")
    
    def get_site_uri(self) -> str:
        return "reddit.com"
    
class HabrHandler(SiteSearchHandler):
    def get_triggers(self) -> tuple[str]:
        return ("habr", "хабр")
    
    def get_site_uri(self) -> str:
        return "habr.com"
    
class WikiHandler(SiteSearchHandler):
    def get_triggers(self) -> tuple[str]:
        return ("wiki", "w", "вики", "в")
    
    def get_site_uri(self) -> str:
        return "wikipedia.org"
    
class WikiCzHandler(SiteSearchHandler):
    def get_triggers(self) -> tuple[str]:
        return ("wikicz", "wcz")
    
    def get_site_uri(self) -> str:
        return "cs.wiktionary.org"
    
class SeznamCzHandler(SiteSearchHandler):
    def get_triggers(self) -> tuple[str]:
        return ("seznamcz", "scz")
    
    def get_site_uri(self) -> str:
        return "slovnik.seznam.cz"
    
class YoutubeHandler(SiteSearchHandler):
    def get_triggers(self) -> tuple[str]:
        return ("youtube", "yt", "ютуб", "в")
    
    def get_site_uri(self) -> str:
        return "youtube.com"
    
class DefaultHandler(SiteSearchHandler):
    def get_triggers(self) -> tuple[str]:
        return ("search", "поиск", "s", "п")
    
    def get_site_uri(self) -> str:
        return ""
    
search_resolver = SearchResolver()
search_resolver.register_handler(StackOverflowHandler())
search_resolver.register_handler(StackExchangeHandler())
search_resolver.register_handler(RedditHandler())
search_resolver.register_handler(HabrHandler())
search_resolver.register_handler(WikiHandler())
search_resolver.register_handler(WikiCzHandler())
search_resolver.register_handler(SeznamCzHandler())
search_resolver.register_handler(YoutubeHandler())
search_resolver.register_handler(DefaultHandler())