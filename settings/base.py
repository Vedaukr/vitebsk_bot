from utils.search_resolver import SearchResolver, SiteSearchHandler


DB_NAME = "app.db"
SQLALCHEMY_TRACK_MODIFICATIONS = True
BOT_NAME = "vitebsk_bot"
BOT_TOKEN = ""

LOGS_PATH = ""
LOGS_FILENAME = "vbot.log"

#openai
OPENAI_ORGANIZATION = "org-DoSOUBT1gIASAWhJm8DRNmVI"
OPENAI_TOKEN = ""

#bing
BING_SUBSCRIPTION_KEY = ""

#rapid_api
RAPID_API_SUBSCRIPTION_KEY = ""

#stabilityai
STABILITYAI_TOKEN = ""

#temp solution for scheduler
TARGET_CHAT_ID = ""

#open weather
OPENWEATHER_API_KEY = ""

# Search resolver register
default_search_resolver = SearchResolver()

# stack-related
so_link_to_header = lambda link: " ".join(link.split('/')[-1].split('-'))
default_search_resolver.register_handler(
    SiteSearchHandler(
        triggers=('so', 'stackoverflow', 'стак', 'со'), 
        site_uri="stackoverflow.com", 
        get_header_func=so_link_to_header
    )
)
default_search_resolver.register_handler(
    SiteSearchHandler(
        triggers=('stex', 'stackexchange', 'стакэкс', 'сэ'), 
        site_uri="stackexchange.com", 
        get_header_func=so_link_to_header
    )
)

# languages related
default_search_resolver.register_handler(SiteSearchHandler(triggers=('wiktionary', 'wkt'), site_uri="wiktionary.org"))
default_search_resolver.register_handler(SiteSearchHandler(triggers=('wikicz', 'wcz'), site_uri="cs.wiktionary.org"))
default_search_resolver.register_handler(SiteSearchHandler(triggers=('seznamcz', 'scz'), site_uri="slovnik.seznam.cz"))
default_search_resolver.register_handler(SiteSearchHandler(triggers=('udict', 'urbandictionary'), site_uri="www.urbandictionary.com"))

# articles
default_search_resolver.register_handler(SiteSearchHandler(triggers=('red', 'reddit', 'ред', 'реддит'), site_uri="reddit.com"))
default_search_resolver.register_handler(SiteSearchHandler(triggers=('wiki', 'w', 'вики', 'в'), site_uri="wikipedia.org"))
default_search_resolver.register_handler(SiteSearchHandler(triggers=('habr', 'хабр'), site_uri="habr.com"))
default_search_resolver.register_handler(SiteSearchHandler(triggers=('hh', 'hnews'), site_uri="news.ycombinator.com"))

# yt/media
default_search_resolver.register_handler(SiteSearchHandler(triggers=('youtube', 'yt', 'ютуб', 'в'), site_uri="youtube.com"))

# standard search
default_search_resolver.register_handler(SiteSearchHandler(triggers=('search', 'поиск', 's', 'п'), site_uri=""))