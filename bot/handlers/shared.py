import base64
import telebot
import logging
import traceback
from typing import Callable
from bot.bot_instance.bot import bot_instance

def create_message(sim_arr, chat_id):
    # fix this smh
    chat_id = normalize_tg_chat_id(chat_id)
    
    res = "I've found some similar memes:\n"
    for sim in sim_arr:
        dist = sim["dist"]
        msd_id = sim["msgId"]
        sim = get_similarity(dist) if dist else "Exact"
        res += f"Link: {get_tg_link(chat_id, msd_id)}, Similarity: {sim}\n"
    return res

def get_tg_link(chat_id, msd_id) -> str:
    return f"https://t.me/c/{chat_id}/{msd_id}"

def get_similarity(dist):
    return str(round((64 - dist)/64, 2))

def get_keyboard(chat_id, msg_id):
    button_1 = telebot.types.InlineKeyboardButton('Fuck off, bot', callback_data=f'f|{chat_id}|{msg_id}')
    button_2 = telebot.types.InlineKeyboardButton('Delete duplicated meme', callback_data=f'r|{chat_id}|{msg_id}')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(button_1)
    keyboard.add(button_2)
    return keyboard

def normalize_tg_chat_id(chat_id):
    return abs(chat_id) % 10 ** 10

def download_img_from_telegram(message: telebot.types.Message) -> bytearray:
    return download_file_from_telegram(message.photo[-1].file_id)

def download_file_from_telegram(file_id: str) -> bytearray:
    file_info = bot_instance.get_file(file_id)
    return bot_instance.download_file(file_info.file_path)

def msg_starts_with_filter(starts_with: tuple[str]) -> Callable[[telebot.types.Message], bool]:
    def filter_lambda(message: telebot.types.Message):
        text = get_msg_text(message).lower()
        return text.startswith(starts_with)
    return filter_lambda

def get_msg_text(message: telebot.types.Message):
    reply_part = ""
    if message.reply_to_message:
        reply_part = f": {get_msg_text(message.reply_to_message)}"

    if message.text:
        return message.text + reply_part
    if message.caption:
        return message.caption
    
    return ""

def try_get_image(message: telebot.types.Message) -> tuple[str, str]:
    if message.photo:
        return get_photo_base64(message.photo[-1].file_id)
    
    if message.reply_to_message and message.reply_to_message.photo:
        return get_photo_base64(message.reply_to_message.photo[-1].file_id)
    
    return (None, None)

def get_photo_base64(fileId: str) -> tuple[str, str]:
    file_info = bot_instance.get_file(fileId)
    img_bytes = bot_instance.download_file(file_info.file_path)
    return base64.b64encode(img_bytes).decode('utf-8'), file_info.file_path.split('.')[-1]

def tg_exception_handler(func):
    logger = logging.getLogger(__name__)
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
            return res
        except Exception as ex:
            message: telebot.types.Message = args[0]
            message.content_type
            logger.error(f'Telegram message: {get_msg_text(message)}\nResulted in following error: \n{traceback.format_exc()}')
            bot_instance.reply_to(message, f'Telegram message: {get_msg_text(message)}\nResulted in following error: \n{ex}')

    return wrapper

def continue_handling(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs)
        return telebot.ContinueHandling()
    return wrapper