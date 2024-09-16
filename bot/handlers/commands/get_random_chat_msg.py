from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import normalize_tg_chat_id
from bot.handlers.shared import tg_exception_handler
import telebot
import numpy as np

MAX_TRIES = 5

@bot_instance.message_handler(commands=['get_random_chat_msg'])
@tg_exception_handler
def get_random_chat_msg(message: telebot.types.Message):
    chat_id = message.chat.id
    current_try = MAX_TRIES
    while current_try > 0:
        current_try -= 1
        try:
            msg_id = np.random.choice(message.id)
            fwd = bot_instance.forward_message(chat_id=chat_id, from_chat_id=chat_id, message_id=msg_id)
            bot_instance.reply_to(message=fwd, text=f"Link: https://t.me/c/{normalize_tg_chat_id(chat_id)}/{msg_id}")
            return
        except Exception as e:
            pass
    raise ValueError(f"Unlucky, {MAX_TRIES} tries ended up in retrieving deleted message.")
