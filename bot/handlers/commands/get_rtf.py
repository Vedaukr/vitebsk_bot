from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import tg_exception_handler
import telebot, random

RTF_CHANELL_ID = -1001632815403
RTF_MSG_COUNT = 15358
MAX_TRIES = 5

@bot_instance.message_handler(commands=['get_rtf'])
@tg_exception_handler
def handle_rtf(message: telebot.types.Message):
    current_try = MAX_TRIES
    while current_try > 0:
        current_try -= 1
        try:
            msg_id = random.randint(0, RTF_MSG_COUNT)
            bot_instance.forward_message(message.chat.id, RTF_CHANELL_ID, msg_id)
            break
        except Exception as e:
            pass
    raise ValueError(f"Unlucky, {MAX_TRIES} tries ended up in retrieving deleted message.")
