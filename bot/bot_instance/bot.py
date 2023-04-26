import telebot
from bot.bot_instance.bot_token import bot_token

bot_instance = telebot.TeleBot(token=bot_token, parse_mode=None)

bot_instance.set_my_commands([
    telebot.types.BotCommand("/ping", "Check if alive (debug)"),
    telebot.types.BotCommand("/get_count", "Check images count in db (debug)"),
    telebot.types.BotCommand("/get_rtf", "Получить пожилого ртфченка"),
    telebot.types.BotCommand("/get_img_labels", "Описание картинки (реплай на картинку)"),
    telebot.types.BotCommand("/get_img_text", "Распознать текст на картинке (реплай на картинку)"),
])
