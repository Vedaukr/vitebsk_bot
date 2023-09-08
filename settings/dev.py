from .base import *
import os, sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI =  f'sqlite:///{os.path.join(BASE_DIR, DB_NAME)}'
BOT_TOKEN = sys.argv[1]

OPENAI_TOKEN = sys.argv[2]
#BING_SUBSCRIPTION_KEY = sys.argv[3]

RAPID_API_SUBSCRIPTION_KEY = sys.argv[3]