from .base import *
import os

BASE_DIR = "/app/data"
SQLALCHEMY_DATABASE_URI =  f'sqlite:///{os.path.join(BASE_DIR, DB_NAME)}'
BOT_TOKEN = os.environ["BOT_TOKEN"] 
LOGS_PATH = os.path.join(BASE_DIR, "logs", LOGS_FILENAME)

PERSISTENT_CACHE_PATH = os.path.join(BASE_DIR, "ctx_cache")
if not os.path.exists(PERSISTENT_CACHE_PATH):
    os.mkdir(PERSISTENT_CACHE_PATH)

OPENAI_TOKEN = os.environ["OPENAI_TOKEN"] 
STABILITYAI_TOKEN = os.environ["STABILITYAI_TOKEN"] 

BING_SUBSCRIPTION_KEY = os.environ["BING_SUBSCRIPTION_KEY"] 
RAPID_API_SUBSCRIPTION_KEY = os.environ["RAPID_API_SUBSCRIPTION_KEY"] 

TARGET_CHAT_ID = os.environ["TARGET_CHAT_ID"] 

OPENWEATHER_API_KEY = os.environ["OPENWEATHER_API_KEY"]

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]

TELEGRAPH_TOKEN = os.environ["TELEGRAPH_TOKEN"]