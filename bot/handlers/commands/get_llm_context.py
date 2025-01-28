from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import tg_exception_handler
import telebot

@bot_instance.message_handler(commands=['get_llm_context'])
@tg_exception_handler
def get_ctx_handler(message: telebot.types.Message):
    pass