import telebot
from settings import BOT_TOKEN

bot_instance = telebot.TeleBot(token=BOT_TOKEN, parse_mode=None)

bot_instance.set_my_commands([
    telebot.types.BotCommand("/ping", "Check if alive (debug)"),
    telebot.types.BotCommand("/get_count", "Check images count in db (debug)"),
    telebot.types.BotCommand("/clear_context", "Clear gpt context"),
    telebot.types.BotCommand("/get_rtf", "Получить пожилого ртфченка"),
    telebot.types.BotCommand("/get_img_labels", "Описание картинки (реплай на картинку)"),
    telebot.types.BotCommand("/get_img_text", "Распознать текст на картинке (реплай на картинку)"),
])
