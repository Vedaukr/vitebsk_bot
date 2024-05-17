from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import tg_exception_handler
from bot.handlers.msg_handlers.shared import get_prompt
from services.search_service import SearchService
from services.liq_service import CsService, DotaService, GameInfo, LiquipediaService
from utils.escape_markdown import escape_markdown
from utils.search_resolver import search_resolver
import telebot, datetime, pytz
import argparse
import funcy as fy

CSGO_TRIGGERS = ("кс", "csgo", "cs")
DOTA_TRIGGERS = ("dota", "дота")
MAX_GAMES = 10

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
    bot_reply = bot_instance.reply_to(message, "searching...")
    prompt = get_prompt(message.text)

    search_handler = search_resolver.get_site_search_handler(prompt=prompt)
    if search_handler:
        search_prompt = get_prompt(prompt)
        if search_prompt:
            links = search_service.get_search_results(search_prompt, search_handler.get_site_uri())
            response = search_handler.get_response(links)
            bot_instance.edit_message_text(response, message.chat.id, bot_reply.message_id, parse_mode="MarkdownV2")
            return None

    try:
        args, arg_prompt = parser.parse_known_args(prompt.lower().split(" "))
        arg_prompt = " ".join(arg_prompt)
        
        if args.command in CSGO_TRIGGERS:
            response = handle_liq_prompt(args, arg_prompt, csgo_service)
            
        if args.command in DOTA_TRIGGERS:
            response = handle_liq_prompt(args, arg_prompt, dota_service)
        
        bot_instance.reply_to(message, response, parse_mode="MarkdownV2", disable_web_page_preview=True)

    except SystemExit:
        bot_instance.reply_to(message, "Invalid bot args, check /help")
    
    finally:
        bot_instance.delete_message(bot_reply.chat.id, bot_reply.message_id)

def handle_liq_prompt(args: argparse.Namespace, prompt: str, game_service: LiquipediaService) -> str:
    today_time = datetime.datetime.now().replace(minute=0, hour=0, second=0, microsecond=0)
    
    FILTER_ACTUAL = lambda game: game.start_time.replace(tzinfo=None) >= today_time
    FILTER_TODAY = lambda game: game.start_time.replace(tzinfo=None).date() == today_time.date()
    FILTER_TEAM = lambda game: prompt in game.team1.lower() or prompt in game.team2.lower()
    FILTER_TOURNAMENT = lambda game: prompt in game.tournament.lower()

    games = game_service.get_upcoming_and_ongoing_games()
    
    filters = [FILTER_ACTUAL]
    if args.today:
        filters.append(FILTER_TODAY)

    if prompt:
        if args.team:
            filters.append(FILTER_TEAM)
        elif args.tournament:
            filters.append(FILTER_TOURNAMENT)
        else:
            filters.append(fy.any_fn(FILTER_TEAM, FILTER_TOURNAMENT))

    games = list(fy.filter(fy.all_fn(*filters), games))
    if not games:
        return "Nothing found"
    
    games = games[:MAX_GAMES]
    game_service.update_stream_links(games)
    return get_games_response(games)

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