from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import tg_exception_handler
from bot.handlers.msg_handlers.shared import get_prompt
from services.search_service import SearchService
from services.cs_service import CsService, GameInfo
from utils.escape_markdown import escape_markdown
from utils.search_resolver import search_resolver
from dateutil import parser
import telebot, datetime, pytz

CSGO_TRIGGERS = ("кс", "csgo", "cs")
MAX_CS_GAMES = 10

PRAGUE_TZ = pytz.timezone("Europe/Prague")
KYIV_TZ = pytz.timezone("Europe/Kiev")

# Singletons
search_service = SearchService()
csgo_service = CsService("Telegram fun bot")

@bot_instance.message_handler(regexp=r"^(\bbot\b|\bбот\b)\s.+")
@tg_exception_handler
def bot_cmd_handler(message: telebot.types.Message):
    prompt = get_prompt(message.text)

    if prompt.startswith(CSGO_TRIGGERS):
        cs_prompt = get_prompt(prompt)
        cs_games = csgo_service.get_upcoming_and_ongoing_games()
        cs_games = filter_unique(cs_games, lambda game: (game.team1, game.team2))

        today_time = datetime.datetime.now().replace(minute=0, hour=0, second=0, microsecond=0)
        cs_games = list(filter(lambda game: game.start_time.replace(tzinfo=None) >= today_time, cs_games))
        
        if cs_prompt:
            team = cs_prompt.lower()
            cs_games = list(filter(lambda game: team in game.team1.lower() or team in game.team2.lower(), cs_games))

        if not cs_games:
            bot_instance.reply_to(message, "Nothing found")
            return None
        
        bot_instance.reply_to(message, get_csgo_response(cs_games[:MAX_CS_GAMES]), parse_mode="MarkdownV2")

    search_handler = search_resolver.get_site_search_handler(prompt=prompt)
    if search_handler:
        search_prompt = get_prompt(prompt)
        if search_prompt:
            bot_reply = bot_instance.reply_to(message, "searching...")
            links = search_service.get_search_results(search_prompt, search_handler.get_site_uri())
            response = search_handler.get_response(links)
            bot_instance.edit_message_text(response, message.chat.id, bot_reply.message_id, parse_mode="MarkdownV2")

def get_csgo_response(games: list[GameInfo]):
    result = ""
    for game in games:
        result += f"[{escape_markdown(game.tournament)}]({escape_markdown(game.tournament_link)})\n"
        result += f"{escape_markdown(game.team1)} \- {escape_markdown(game.team2)}\n"
        
        if game.start_time:
            pg_time = game.start_time.astimezone(PRAGUE_TZ)
            kyiv_time = game.start_time.astimezone(KYIV_TZ)
            time_str = f"{pg_time.strftime('%d %b %Y')} / {pg_time.strftime('%H:%M')} European / {kyiv_time.strftime('%H:%M')} Kyiv"
            result += f"{escape_markdown(time_str)}\n"
        
        if game.twitch_channel:
            result += f"[{'Twitch'}]({escape_markdown(game.twitch_channel)})\n"
        
        if game.youtube_channel:
            result += f"[{'Youtube'}]({escape_markdown(game.youtube_channel)})\n"

        result += "\n"

    return result

def filter_unique(base_list, getter_func):
    helper_dict = {}
    for el in base_list:
        comparing_element = getter_func(el)
        if comparing_element in helper_dict:
            continue
        helper_dict[comparing_element] = el

    return list(helper_dict.values())