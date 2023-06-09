from abc import ABC, abstractmethod
from utils.singleton import Singleton
from utils.escape_markdown import escape_markdown

class SiteSearchHandler(ABC):

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
            message += f"{count + 1}\. [{escape_markdown(header)}]({link})\n"
        return message
    
    def get_link_header(self, link: str) -> str:
        return link
    
class SearchResolver(metaclass=Singleton):
    def __init__(self) -> None:
        self.handlers = []

    def register_handler(self, handler: SiteSearchHandler):
        self.handlers.append(handler)

    def get_site_search_handler(self, prompt: str) -> SiteSearchHandler:
        for handler in self.handlers:
            if prompt.startswith(handler.get_triggers()):
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
search_resolver.register_handler(DefaultHandler())