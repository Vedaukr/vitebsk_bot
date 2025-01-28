from bot.bot_instance.bot import bot_instance
import telebot
from bot.handlers.shared import tg_exception_handler

@bot_instance.message_handler(commands=['clear_llm_context'])
@tg_exception_handler
def clr_handler(message: telebot.types.Message):
    bot_instance.reply_to(message, "Context cleared.")