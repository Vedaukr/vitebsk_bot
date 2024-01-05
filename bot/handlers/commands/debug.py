from bot.bot_instance.bot import bot_instance
from services.db_service import DbService
from bot.handlers.shared import tg_exception_handler
import telebot

db_service = DbService()

@bot_instance.message_handler(commands=['ping'])
@tg_exception_handler
def handle_ping(message: telebot.types.Message):
    bot_instance.reply_to(message, "Alive")

@bot_instance.message_handler(commands=['get_img_count'])
@tg_exception_handler
def handle_image_count(message: telebot.types.Message):
    bot_instance.reply_to(message, db_service.get_images_count(str(message.chat.id)))

@bot_instance.message_handler(commands=['test_exception_handling'])
@tg_exception_handler
def handle_image_count(message: telebot.types.Message):
    raise Exception("Exception")