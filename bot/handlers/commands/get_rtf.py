from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import tg_exception_handler
import telebot, random

RTF_CHANELL_ID = -1001632815403
RTF_MSG_COUNT = 15358

@bot_instance.message_handler(commands=['get_rtf'])
@tg_exception_handler
def handle_rtf(message: telebot.types.Message):
    while True:
        try:
            msg_id = random.randint(0, RTF_MSG_COUNT)
            bot_instance.forward_message(message.chat.id, RTF_CHANELL_ID, msg_id)
            break
        except Exception as e:
            print(e)
