from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import tg_exception_handler
from bot.handlers.msg_handlers.shared import get_prompt
from services.search_service import SearchService
from services.liq_service import CsService, DotaService, GameInfo
from utils.escape_markdown import escape_markdown
from utils.search_resolver import search_resolver
import telebot, datetime, pytz
import argparse

CSGO_TRIGGERS = ("кс", "csgo", "cs")
DOTA_TRIGGERS = ("dota", "дота")
MAX_GAMES = 8

PRAGUE_TZ = pytz.timezone("Europe/Prague")
KYIV_TZ = pytz.timezone("Europe/Kiev")

# Singletons
search_service = SearchService()
csgo_service = CsService("Telegram fun bot")
dota_service = DotaService("Telegram fun bot")

parser = argparse.ArgumentParser(prog='bot')
subparsers = parser.add_subparsers(dest='command')

# csgo
csgo_subparser = subparsers.add_parser(CSGO_TRIGGERS[0], aliases=CSGO_TRIGGERS[1:])
csgo_subparser.add_argument('-team', help='Search by team', default=False, action=argparse.BooleanOptionalAction)
csgo_subparser.add_argument('-tournament', help='Search by tournament', default=False, action=argparse.BooleanOptionalAction)
csgo_subparser.add_argument('-today', help='Only matches that occur today', default=False, action=argparse.BooleanOptionalAction)


# dota
dota_subparser = subparsers.add_parser(DOTA_TRIGGERS[0], aliases=DOTA_TRIGGERS[1:])
dota_subparser.add_argument('-team', help='Search by team', default=False, action=argparse.BooleanOptionalAction)
dota_subparser.add_argument('-tournament', help='Search by tournament', default=False, action=argparse.BooleanOptionalAction)
dota_subparser.add_argument('-today', help='Only matches that occur today', default=False, action=argparse.BooleanOptionalAction)

# # tiktok
# tt_subparser = subparsers.add_parser(TIKTOK_TRIGGERS[0], aliases=TIKTOK_TRIGGERS[1:])
# csgo_subparser.add_argument('last', nargs='?', help='Get last n-th tiktok', type=int, default=1)
# csgo_subparser.add_argument('rnd', nargs='?', help='Get random tiktok', default=False, action=argparse.BooleanOptionalAction)


@bot_instance.message_handler(regexp=r"^(\bbot\b|\bбот\b)\s.+")
@tg_exception_handler
def bot_cmd_handler(message: telebot.types.Message):
    prompt = get_prompt(message.text)

    search_handler = search_resolver.get_site_search_handler(prompt=prompt)
    if search_handler:
        search_prompt = get_prompt(prompt)
        if search_prompt:
            bot_reply = bot_instance.reply_to(message, "searching...")
            links = search_service.get_search_results(search_prompt, search_handler.get_site_uri())
            response = search_handler.get_response(links)
            bot_instance.edit_message_text(response, message.chat.id, bot_reply.message_id, parse_mode="MarkdownV2")
            return None

    try:
        args, arg_prompt = parser.parse_known_args(prompt.lower().split(" "))
        arg_prompt = " ".join(arg_prompt)
        
        if args.command in CSGO_TRIGGERS:
            handle_cs_prompt(message, args, arg_prompt)
            
        if args.command in DOTA_TRIGGERS:
            handle_dota_prompt(message, args, arg_prompt)

    except SystemExit:
        bot_instance.reply_to(message, parser.format_help())

    

def handle_cs_prompt(message: telebot.types.Message, args: argparse.Namespace, cs_prompt: str):
    cs_games = csgo_service.get_upcoming_and_ongoing_games()
    cs_games = filter_unique(cs_games, lambda game: (game.team1, game.team2))

    today_time = datetime.datetime.now().replace(minute=0, hour=0, second=0, microsecond=0)
    filter_lambda = lambda game: game.start_time.replace(tzinfo=None) >= today_time
    if args.today:
        filter_lambda = lambda game: game.start_time.replace(tzinfo=None).date() == today_time.date()
    
    cs_games = list(filter(filter_lambda, cs_games))

    team_filter = lambda game: cs_prompt in game.team1.lower() or cs_prompt in game.team2.lower()
    tournament_filter = lambda game: cs_prompt in game.tournament.lower()

    if cs_prompt:
        if args.team:
            cs_games = list(filter(team_filter, cs_games))
        elif args.tournament:
            cs_games = list(filter(tournament_filter, cs_games))
        else:
            try_filter = list(filter(team_filter, cs_games))
            if not try_filter:
                try_filter = list(filter(tournament_filter, cs_games))
            cs_games = try_filter

    if not cs_games:
        bot_instance.reply_to(message, "Nothing found")
        return None
    
    cs_games = cs_games[:MAX_GAMES]
    csgo_service.update_stream_links(cs_games)
    bot_instance.reply_to(message, get_games_response(cs_games), parse_mode="MarkdownV2")

def handle_dota_prompt(message: telebot.types.Message, args: argparse.Namespace, dota_prompt: str):
    dota_games = dota_service.get_upcoming_and_ongoing_games()
    dota_games = filter_unique(dota_games, lambda game: (game.team1, game.team2))

    today_time = datetime.datetime.now().replace(minute=0, hour=0, second=0, microsecond=0)
    filter_lambda = lambda game: game.start_time.replace(tzinfo=None) >= today_time
    if args.today:
        filter_lambda = lambda game: game.start_time.replace(tzinfo=None).date() == today_time.date()
    
    dota_games = list(filter(filter_lambda, dota_games))

    team_filter = lambda game: dota_prompt in game.team1.lower() or dota_prompt in game.team2.lower()
    tournament_filter = lambda game: dota_prompt in game.tournament.lower()

    if dota_prompt:
        if args.team:
            dota_games = list(filter(team_filter, dota_games))
        elif args.tournament:
            dota_games = list(filter(tournament_filter, dota_games))
        else:
            try_filter = list(filter(team_filter, dota_games))
            if not try_filter:
                try_filter = list(filter(tournament_filter, dota_games))
            dota_games = try_filter

    if not dota_games:
        bot_instance.reply_to(message, "Nothing found")
        return None
    
    dota_games = dota_games[:MAX_GAMES]
    dota_service.update_stream_links(dota_games)
    bot_instance.reply_to(message, get_games_response(dota_games), parse_mode="MarkdownV2")

def get_games_response(games: list[GameInfo]):
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