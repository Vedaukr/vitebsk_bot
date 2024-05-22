from typing import Callable
from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import tg_exception_handler
from bot.handlers.msg_handlers.shared import get_prompt
from services.search_service import SearchService
from services.liq_service import CsService, DotaService, GameInfo, LiquipediaService
from utils.md_utils import escape_markdown
from utils.search_resolver import search_resolver
import telebot, datetime, pytz
import argparse
import funcy as fy

CS_TRIGGERS = ("кс", "cs", "cs")
DOTA_TRIGGERS = ("dota", "дота")

PRAGUE_TZ = pytz.timezone("Europe/Prague")
KYIV_TZ = pytz.timezone("Europe/Kiev")

# Singletons
search_service = SearchService()
cs_service = CsService("Telegram fun bot")
dota_service = DotaService("Telegram fun bot")

parser = argparse.ArgumentParser(prog='bot')
subparsers = parser.add_subparsers(dest='command')

# cs
cs_subparser = subparsers.add_parser(CS_TRIGGERS[0], aliases=CS_TRIGGERS[1:])
cs_subparser.add_argument('-team', help='Search by team', default=False, action=argparse.BooleanOptionalAction)
cs_subparser.add_argument('-tournament', help='Search by tournament', default=False, action=argparse.BooleanOptionalAction)
cs_subparser.add_argument('-today', help='Only matches that occur today', default=False, action=argparse.BooleanOptionalAction)
cs_subparser.add_argument('-yt', help='Only matches that have youtube stream', default=False, action=argparse.BooleanOptionalAction)
cs_subparser.add_argument('-twitch', help='Only matches that have twitch stream', default=False, action=argparse.BooleanOptionalAction)


# dota
dota_subparser = subparsers.add_parser(DOTA_TRIGGERS[0], aliases=DOTA_TRIGGERS[1:])
dota_subparser.add_argument('-team', help='Search by team', default=False, action=argparse.BooleanOptionalAction)
dota_subparser.add_argument('-tournament', help='Search by tournament', default=False, action=argparse.BooleanOptionalAction)
dota_subparser.add_argument('-today', help='Only matches that occur today', default=False, action=argparse.BooleanOptionalAction)
dota_subparser.add_argument('-yt', help='Only matches that have youtube stream', default=False, action=argparse.BooleanOptionalAction)
dota_subparser.add_argument('-twitch', help='Only matches that have twitch stream', default=False, action=argparse.BooleanOptionalAction)


@bot_instance.message_handler(regexp=r"^(\bbot\b|\bбот\b)\s.+")
@tg_exception_handler
def bot_cmd_handler(message: telebot.types.Message):
    bot_reply = bot_instance.reply_to(message, "searching...")
    prompt = get_prompt(message.text)

    search_handler = search_resolver.get_site_search_handler(prompt=prompt)
    if search_handler:
        search_prompt = get_prompt(prompt)
        if search_prompt:
            links = search_service.get_search_results(search_prompt, search_handler.get_site_uri())
            response = search_handler.get_response(links)
            bot_instance.edit_message_text(response, message.chat.id, bot_reply.message_id, parse_mode="MarkdownV2", disable_web_page_preview=True)
            return None

    try:
        args, arg_prompt = parser.parse_known_args(prompt.lower().split(" "))
        arg_prompt = " ".join(arg_prompt)
        
        if args.command in CS_TRIGGERS:
            response = handle_liq_prompt(cs_service, args, arg_prompt)
            
        if args.command in DOTA_TRIGGERS:
            response = handle_liq_prompt(dota_service, args, arg_prompt)
        
        bot_instance.reply_to(message, response, parse_mode="MarkdownV2", disable_web_page_preview=True)

    except SystemExit:
        bot_instance.reply_to(message, "Invalid bot args, check /help")
    
    finally:
        bot_instance.delete_message(bot_reply.chat.id, bot_reply.message_id)

def handle_liq_prompt(game_service: LiquipediaService, args: argparse.Namespace, prompt: str) -> str:
    filters = build_filters(args, prompt)
    games = game_service.get_upcoming_and_ongoing_games(filters)

    if not games:
        return "Nothing found"
    
    return ''.join(map(lambda g: g.to_md_string(), games))

def build_filters(args: argparse.Namespace, prompt: str) -> list[Callable[[GameInfo], bool]]:
    today_time = datetime.datetime.now().replace(minute=0, hour=0, second=0, microsecond=0)
    
    FILTER_ACTUAL = lambda game: game.start_time.replace(tzinfo=None) >= today_time
    FILTER_TODAY = lambda game: game.start_time.replace(tzinfo=None).date() == today_time.date()
    FILTER_TEAM = lambda game: prompt in game.team1.lower() or prompt in game.team2.lower()
    FILTER_TOURNAMENT = lambda game: prompt in game.tournament.lower()
    FILTER_YT = lambda game: game.stream_links and any(map(lambda k: k.startswith("youtube"), game.stream_links.keys()))
    FILTER_TWITCH = lambda game: game.stream_links and any(map(lambda k: k.startswith("twitch"), game.stream_links.keys()))
    
    filters = [FILTER_ACTUAL]
    if args.today:
        filters.append(FILTER_TODAY)

    if args.yt:
        filters.append(FILTER_YT)
        
    if args.twitch:
        filters.append(FILTER_TWITCH)

    if prompt:
        if args.team:
            filters.append(FILTER_TEAM)
        elif args.tournament:
            filters.append(FILTER_TOURNAMENT)
        else:
            filters.append(fy.any_fn(FILTER_TEAM, FILTER_TOURNAMENT))

    return filters