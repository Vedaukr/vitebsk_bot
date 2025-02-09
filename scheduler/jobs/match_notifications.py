import datetime
import pytz
from bot.bot_instance.bot import bot_instance
from services.liq_service import CsService, DotaService, GameInfo
from scheduler.bot_scheduler import scheduler_instance
from settings import settings

TARGET_CHAT_ID = settings["TARGET_CHAT_ID"]

HOUR = 60*60
TEAM_NAMES = ["navi", "natus vincere", "passion ua", "b8"]

PRAGUE_TZ = pytz.timezone("Europe/Prague")
KYIV_TZ = pytz.timezone("Europe/Kiev")

cs_service = CsService("Telegram fun bot")
dota_service = DotaService("Telegram fun bot")

@scheduler_instance.scheduled_job(trigger="interval", seconds=HOUR/2)
def match_notification_job():
    FILTER_IN_1_HOUR = lambda game: -HOUR/4 < (game.start_time.astimezone(PRAGUE_TZ) - datetime.datetime.now().astimezone(PRAGUE_TZ)).total_seconds() < HOUR 
    FILTER_TEAM = lambda game: any(map(lambda t: t == game.team1.lower() or t == game.team2.lower(), TEAM_NAMES))
    
    filters = [FILTER_IN_1_HOUR, FILTER_TEAM]

    cs_games = cs_service.get_upcoming_and_ongoing_games(filters=filters)
    if cs_games:
        bot_instance.send_message(TARGET_CHAT_ID, get_response(cs_games, "CS2"), parse_mode="MarkdownV2", disable_web_page_preview=True)

    dota_games = dota_service.get_upcoming_and_ongoing_games(filters=filters)
    if dota_games:
        bot_instance.send_message(TARGET_CHAT_ID, get_response(dota_games, "Dota2"), parse_mode="MarkdownV2", disable_web_page_preview=True)

def get_response(games: list[GameInfo], game_name) -> str:
    return f"Upcoming/ongoing {game_name} matches:\n\n{''.join(map(lambda g: g.to_md_string(), games))}"