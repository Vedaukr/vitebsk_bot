from urllib.parse import unquote
from typing import Callable, Optional
from utils.singleton import Singleton
from utils.md_utils import escape_markdown
import requests, re, logging, html

logger = logging.getLogger(__name__)

class SiteSearchHandler:
    def __init__(self, 
                 triggers: tuple[str], 
                 site_uri: str, 
                 get_header_func: Optional[Callable[[str], str]] = None) -> None:
        
        self.headers = {
            'Authorization': 'authorization',
            'cookie': 'hl=en'
        }
        self.cookies = {'CONSENT': 'YES+1'}
        self._triggers = triggers
        self._site_uri = site_uri
        self._get_header_func = get_header_func

    @property
    def triggers(self) -> tuple[str]:
        return self._triggers
    
    @property
    def site_uri(self) -> str:
        return self._site_uri

    def get_response(self, links: list[str]) -> str:
        message = "Results:\n"
        for count,link in enumerate(links):
            header = self.get_link_header(link)
            if not header:
                header = "Untitled"
            header = unquote(header)
            message += f"{count + 1}\. [{escape_markdown(header)}]({escape_markdown(link)})\n"
        return message
    
    def get_link_header(self, link: str) -> str:
        header = self.try_get_header_from_html(link)
        if not header and self._get_header_func:
            header = self._get_header_func(link)
        return header or link.split('/')[-1]
    
    def try_get_header_from_html(self, link: str) -> str:
        try:
            response = requests.get(link, timeout=5, headers=self.headers, cookies=self.cookies)
            response.raise_for_status()
            pattern = r"<title>(.*?)</title>"
            match = re.search(pattern, response.text)
            if match:
                return html.unescape(match.group(1))
        except Exception as e:
            logger.error(f"Error while trying to get header from link {link}:\n{e}.")

class SearchResolver(metaclass=Singleton):
    def __init__(self) -> None:
        self.handlers: list[SiteSearchHandler] = []

    def register_handler(self, handler: SiteSearchHandler):
        self.handlers.append(handler)

    def get_site_search_handler(self, prompt: str) -> SiteSearchHandler:
        prompt = prompt.split(" ")[0]
        for handler in self.handlers:
            if prompt.lower() in handler.triggers:
                return handler