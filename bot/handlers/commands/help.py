from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import tg_exception_handler
import telebot
from settings.base import default_search_resolver

@bot_instance.message_handler(commands=['help'])
@tg_exception_handler
def get_bot_triggers(message: telebot.types.Message):
    bot_instance.reply_to(message, help_message)

search_triggers = "Search triggers:\n"
for handler in default_search_resolver.handlers:
    uri = handler.site_uri
    search_triggers += f"Site: {uri if uri else 'Default search'}, Triggers: {handler.triggers}\n"

help_message = rf'''
GPT:

version 4o mini (text + image), reply to message with photo also works::
gpt [prompt]

version 40 (text + image), reply to message with photo also works:
gpt4 [prompt]

Use /get_available_openai_models to see full list of models, 
you can try any from the list, no guarantee that it will work though:
gpt-4o-realtime-preview [prompt]

Claude:

Default, uses haiku
claude [prompt]

Cheapest
haiku [prompt] 

Workable
sonnet [prompt]

Expensive as fuck
opus [prompt]

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
city_name has to be written in quotation marks if consists from 2+ words e.g. "Kryvyi Rih"

'''