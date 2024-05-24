from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import tg_exception_handler
import telebot
from utils.search_resolver import search_resolver

@bot_instance.message_handler(commands=['help'])
@tg_exception_handler
def get_bot_triggers(message: telebot.types.Message):
    bot_instance.reply_to(message, help_message)

search_triggers = "Search triggers:\n"
for handler in search_resolver.handlers:
    uri = handler.get_site_uri()
    search_triggers += f"Site: {uri if uri else 'Default search'}, Triggers: {handler.get_triggers()}\n"

help_message = rf'''
GPT:

version 3.5 (only text):
gpt [prompt]

version 4 (text + image), reply to message with photo also works:
gpt4 [prompt]

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

{search_triggers}
Image generation:

Low-cost version:
sd [prompt]
sdlow [prompt]

High-cost version:
sdcore [prompt]

Weather:

bot [wf|weather] [city_name] [date]
date is optional, supports forecasts up to 5 days
city_name should be written in quotation marks if consists from 2+ words e.g. "Kryvyi Rih"

'''