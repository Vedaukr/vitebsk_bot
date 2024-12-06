from .telebot_extention import TelebotExt
from settings import BOT_TOKEN
import telebot

bot_instance = TelebotExt(token=BOT_TOKEN, parse_mode=None)

bot_instance.set_my_commands([
    telebot.types.BotCommand("/clear_gpt_context", "Clear gpt context"),
    telebot.types.BotCommand("/get_gpt_context", "View my gpt context"),
    telebot.types.BotCommand("/get_available_openai_models", "View available openai models"),
    telebot.types.BotCommand("/get_dementia_rating", "Dementia rating"),
    telebot.types.BotCommand("/get_rtf", "Получить пожилого ртфченка"),
    telebot.types.BotCommand("/get_gpt_params", "GPT parameters (list, comment, range)"),
    telebot.types.BotCommand("/reset_gpt_params", "Reset GPT parameters to default (retards from chat have set some shit values)"),
    telebot.types.BotCommand("/get_random_chat_msg", "Рандомное сообщение из чата"),
    telebot.types.BotCommand("/help", "Че ботяра умеет"),
])