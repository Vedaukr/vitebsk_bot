import telebot
from bot.bot_instance.bot import bot_instance

def create_message(sim_arr, chat_id):
    # fix this smh
    chat_id = normalize_tg_chat_id(chat_id)
    
    res = "I've found some similar memes:\n"
    for sim in sim_arr:
        dist = sim["dist"]
        msgId = sim["msgId"]
        sim = get_similarity(dist) if dist else "Exact"
        res += f"Link: https://t.me/c/{chat_id}/{msgId}, Similarity: {sim}\n"
    return res

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

def tg_exception_handler(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as ex:
            exception_report = {
                "event": {
                    "method": func.__name__,
                    "message": str(ex),
                    "args": args,
                    "kwargs": kwargs
                }
            }

            message = args[0]
            print('exception_report ', exception_report)
            bot_instance.reply_to(message, f"Something fucked up: {str(ex.with_traceback(None))}\nException report:\n {exception_report}")

    return wrapper