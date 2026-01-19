from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import tg_exception_handler, continue_handling
import telebot

BLACKLIST = {
    307824319: "бодя",
    #451234616: "картуZ",
    395366648: "гнильня"
}

reply_template = """
⚠️⚠️⚠️ ALERT ⚠️⚠️⚠️
⚠️⚠️⚠️ ALERT ⚠️⚠️⚠️
⚠️⚠️⚠️ ALERT ⚠️⚠️⚠️


Potential bullshit from {}


⚠️⚠️⚠️ ALERT ⚠️⚠️⚠️
⚠️⚠️⚠️ ALERT ⚠️⚠️⚠️
⚠️⚠️⚠️ ALERT ⚠️⚠️⚠️
"""

def msg_contains_url(message: telebot.types.Message) -> bool:
    if message.entities:
        for entity in message.entities:
            if entity.type == 'url':
                return True
    return False

@bot_instance.message_handler(func=msg_contains_url)
@tg_exception_handler
@continue_handling
def handler(message: telebot.types.Message):
    if message.from_user.id in BLACKLIST:
        reply_msg = reply_template.format(username= BLACKLIST[message.from_user.id])
        bot_instance.reply_to(message, reply_msg)

