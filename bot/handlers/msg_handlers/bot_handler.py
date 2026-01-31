from typing import Any, Callable
from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import msg_starts_with_filter, tg_exception_handler
from bot.handlers.configs.search_config import default_search_resolver
from bot.handlers.msg_handlers.shared import get_prompt
from services.owm_service import OwmService
from services.search_service import SearchService
from services.liq_service import CsService, DotaService, GameInfo, LiquipediaService
from services.tz_service import TzService
from utils.md_utils import escape_markdown
import dateutil
import telebot, datetime
import argparse
import funcy as fy
import pytz
import csv

CS_TRIGGERS = ("кс", "cs", "cs")
DOTA_TRIGGERS = ("dota", "дота")
WF_TRIGGERS = ("wf", "weather", "погода")

# Singletons
search_service = SearchService()
cs_service = CsService("Telegram fun bot")
dota_service = DotaService("Telegram fun bot")
tz_service = TzService()
wf_service = OwmService()

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

# wf
wf_subparser = subparsers.add_parser(WF_TRIGGERS[0], aliases=WF_TRIGGERS[1:])
wf_subparser.add_argument('city', help='City name')
wf_subparser.add_argument('date', help='Forecast date', nargs='*', default=None)

@bot_instance.message_handler(func=msg_starts_with_filter(("bot ", "бот ")))
@tg_exception_handler
def bot_cmd_handler(message: telebot.types.Message):
    bot_reply = bot_instance.reply_to(message, "handling...")
    prompt = get_prompt(message.text)

    search_handler = default_search_resolver.get_site_search_handler(prompt=prompt)
    if search_handler:
        search_prompt = get_prompt(prompt)
        if search_prompt:
            links = search_service.get_search_results(search_prompt, search_handler.site_uri)
            response = search_handler.get_response(links)
            bot_instance.edit_message_text(response, message.chat.id, bot_reply.message_id, parse_mode="MarkdownV2", disable_web_page_preview=True)
            return None

    try:
        argslist = [
            x
            for xs in csv.reader([prompt.lower()], skipinitialspace=True, delimiter=" ")
            for x in xs
        ]
        args, arg_prompt = parser.parse_known_args(argslist)
        arg_prompt = " ".join(arg_prompt)
        
        if args.command in CS_TRIGGERS:
            response = handle_liq_prompt(cs_service, args, arg_prompt)
            
        if args.command in DOTA_TRIGGERS:
            response = handle_liq_prompt(dota_service, args, arg_prompt)

        if args.command in WF_TRIGGERS:
            response = handle_wf_prompt(args)
        
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

def handle_wf_prompt(args: argparse.Namespace) -> str:
    if not args.date:
        observation = wf_service.get_weather_at_place(args.city)
        loc = observation.location
        city = f"{loc.name}, {loc.country}"
        target_tz = pytz.timezone(tz_service.get_timezone(loc.lat, loc.lon))
        if observation:
            return get_wf_response([observation.weather], city, target_tz)
        else:
            return "Nothing found"
    
    prompt_date = parse_wf_date(" ".join(args.date))
    forecaster = wf_service.get_weather_forecast(args.city)
    loc = forecaster.forecast.location
    city = f"{loc.name}, {loc.country}"
    target_tz = pytz.timezone(tz_service.get_timezone(loc.lat, loc.lon))
    weathers = list(filter(lambda w: datetime.datetime.fromtimestamp(w.ref_time).date() == prompt_date, forecaster.forecast.weathers))
    if weathers:
        return get_wf_response(weathers, city, target_tz)
    else:
        return "Nothing found"
    
def get_wf_response(weathers: list[Any], city: str, target_tz: Any) -> str:
    full_info = len(weathers) == 1
    date = datetime.datetime.fromtimestamp(weathers[0].ref_time).date()
    result = f"Weather forecast in {city} for {date.strftime('%d %b %Y')}:\n"

    for weather in weathers:
        time = datetime.datetime.fromtimestamp(weather.ref_time).astimezone(target_tz)
        result += f"{time.strftime('%H:%M')}\n"
        result += f"Status: {weather.detailed_status}\n"

        temperature = weather.temperature('celsius')
        result += f"Temperature (feels like): {temperature['temp']} ({temperature['feels_like']})\n"
        result += f"Precipitation probability: {weather.precipitation_probability if weather.precipitation_probability else 'no info'}\n"
        result += f"Cloudiness: {weather.clouds}%\n"
        result += f"Wind speed: {weather.wind().get('speed', 0)} m/s\n"

        if full_info:
            result += f"Humidity: {weather.humidity}%\n"
            srise_time = datetime.datetime.fromtimestamp(weather.srise_time).astimezone(target_tz)
            sset_time = datetime.datetime.fromtimestamp(weather.sset_time).astimezone(target_tz)
            result += f"Sunrise: {srise_time.strftime('%H:%M')}\n"
            result += f"Sunset: {sset_time.strftime('%H:%M')}\n"
        
        result += '\n'

    return escape_markdown(result)

def parse_wf_date(date_str: str) -> datetime.date:
    if date_str == 'today':
        return datetime.datetime.today().date()
    if date_str == 'tomorrow':
        return (datetime.datetime.today() + datetime.timedelta(days=1)).date()
    return dateutil.parser.parse(date_str).date()