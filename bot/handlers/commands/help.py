import itertools
from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import tg_exception_handler
import telebot
from bot.handlers.configs.search_config import default_search_resolver
from bot.handlers.configs.llm_config import default_model_mapping

@bot_instance.message_handler(commands=['help'])
@tg_exception_handler
def get_bot_triggers(message: telebot.types.Message):
    bot_instance.reply_to(message, help_message)


@bot_instance.message_handler(commands=['get_search_triggers'])
@tg_exception_handler
def get_search_triggers(message: telebot.types.Message):
    bot_instance.reply_to(message, search_triggers_msg)


@bot_instance.message_handler(commands=['get_llm_triggers'])
@tg_exception_handler
def get_llm_triggers(message: telebot.types.Message):
    bot_instance.reply_to(message, llm_triggers_msg)


search_triggers_msg = "Search:\nbot [trigger] [trigger_prompt]\nSearch triggers:"
for handler in default_search_resolver.handlers:
    uri = handler.site_uri
    search_triggers_msg += f"Site: {uri if uri else 'Default search'}, Triggers: {handler.triggers}\n"


llm_triggers_msg = rf'''
LLMs:
[llm_trigger] [prompt]
Supports photos, reply to message with photo also works.
Supports full context, like in browser (without images for now) up to 10 messages.
Supported models (Image support: Y if supported otherwise N):'''
models_info = list(default_model_mapping.items())
models_info.sort(key=lambda p: p[1].company_name)
for company_name, models in itertools.groupby(models_info, key=lambda p: p[1].company_name):
    llm_triggers_msg += f'\n\nLLM models from {company_name}:'
    for model_trigger, model_obj in models:
        img_support = 'Y' if model_obj.is_vision_model else 'N'
        llm_triggers_msg += f'\n{model_trigger} [prompt] ({model_obj.model_name}, Images: {img_support}) '


help_message = rf'''
LLMs:
[llm_trigger] [prompt]
/get_llm_triggers

CS/Dota matches:

bot cs [-today|-tournament|-team|-yt|-twitch] [prompt]
bot dota [-today|-tournament|-team|-yt|-twitch] [prompt]
    -today: games that occur today
    -tournament: filter only by tournament 
    -team: filter only by team 
    -yt: only games that have youtube stream
    -twitch: only games that have twitch stream

Search:
bot [trigger] [trigger_prompt]
/get_search_triggers

Image generation:

Low-cost version:
sd [prompt]
sdlow [prompt]

High-cost version:
sdcore [prompt]

Weather:

bot [wf|weather] [city_name] [date]
date is optional, supports forecasts up to 5 days
city_name has to be written in quotation marks if consists from 2+ words e.g. "Kryvyi Rih"

'''