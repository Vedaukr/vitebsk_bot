from .base import *
import os

BASE_DIR = "/app/data"
SQLALCHEMY_DATABASE_URI =  f'sqlite:///{os.path.join(BASE_DIR, DB_NAME)}'
BOT_TOKEN = os.environ["BOT_TOKEN"] 

OPENAI_TOKEN = os.environ["OPENAI_TOKEN"] 
STABILITYAI_TOKEN = os.environ["STABILITYAI_TOKEN"] 

BING_SUBSCRIPTION_KEY = os.environ["BING_SUBSCRIPTION_KEY"] 
RAPID_API_SUBSCRIPTION_KEY = os.environ["RAPID_API_SUBSCRIPTION_KEY"] 