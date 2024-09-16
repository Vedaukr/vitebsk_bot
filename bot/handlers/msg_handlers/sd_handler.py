
from requests import HTTPError
from bot.bot_instance.bot import bot_instance
from bot.handlers.msg_handlers.shared import get_prompt
from bot.handlers.shared import tg_exception_handler, continue_handling, msg_starts_with_filter, get_msg_text
from services.stabilityai_service import StabilityAiService
import telebot

# Singletons
stabilityai_service = StabilityAiService()

@bot_instance.message_handler(func=msg_starts_with_filter(("sd ", "sdlow ")))
@tg_exception_handler
@continue_handling
def sd_handler(message: telebot.types.Message):
    bot_reply = bot_instance.reply_to(message, "generating...")    
    msg_text = get_msg_text(message)
    prompt = get_prompt(msg_text)
    try:
        img_bytes = stabilityai_service.generate_image(prompt)
        bot_instance.send_photo(photo=img_bytes, chat_id=message.chat.id, reply_to_message_id=message.message_id)
    except HTTPError as e:
        bot_instance.reply_to(message, f"Stability UI error: {str(e)}")
    finally:
        bot_instance.delete_message(bot_reply.chat.id, bot_reply.message_id)