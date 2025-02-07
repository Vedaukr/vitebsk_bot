from .base import *
import os, sys, json
import pathlib

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI =  f'sqlite:///{os.path.join(BASE_DIR, "..", "database", DB_NAME)}'
LOGS_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "logs", LOGS_FILENAME))
PERSISTENT_CACHE_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "ctx_cache"))

with open(f"{pathlib.Path.cwd()}\\api-tokens.json") as api_tokens_file:
    api_tokens = json.load(api_tokens_file)
    OPENAI_TOKEN = api_tokens["OPENAI_TOKEN"]
    BOT_TOKEN = api_tokens["BOT_TOKEN"]
    RAPID_API_SUBSCRIPTION_KEY = api_tokens["RAPID_API_SUBSCRIPTION_KEY"]
    STABILITYAI_TOKEN = api_tokens["STABILITYAI_TOKEN"]
    TARGET_CHAT_ID = api_tokens["TARGET_CHAT_ID"]
    OPENWEATHER_API_KEY = api_tokens["OPENWEATHER_API_KEY"]
    ANTHROPIC_API_KEY = api_tokens["ANTHROPIC_API_KEY"]
    DEEPSEEK_API_KEY = api_tokens["DEEPSEEK_API_KEY"]
    TELEGRAPH_TOKEN = api_tokens["TELEGRAPH_TOKEN"]