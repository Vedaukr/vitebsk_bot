from bot.bot_instance.bot import bot_instance
from services.db_service import DbService
from services.labeling_service import LabelingService
from bot.handlers.shared import normalize_tg_chat_id
import random, telebot
import numpy as np

db_service = DbService()
label_service = LabelingService()

DUMP_CHANNEL_ID = -1001947434925
MAX_TRIES = 5

@bot_instance.message_handler(commands=['get_img_labels'])
def handle_labels(message: telebot.types.Message):
    if handle_img_request(message):
        img_bytes = download_img_from_telegram(message.reply_to_message)
        labels = label_service.get_labels(img_bytes)
        lab_msg = "\n".join(labels)
        msg = f"Labels:\n{ lab_msg }"
        bot_instance.reply_to(message, msg)

@bot_instance.message_handler(commands=['get_img_text'])
def handle_text(message: telebot.types.Message):
    if handle_img_request(message):
        img_bytes = download_img_from_telegram(message.reply_to_message)
        texts = label_service.get_text(img_bytes)
        text_msg = "\n".join(texts)
        msg = f"Text:\n{ text_msg }"
        bot_instance.reply_to(message, msg)

def handle_img_request(message: telebot.types.Message) -> bool:
    if not message.reply_to_message:
        bot_instance.reply_to(message, "Use command as a reply to picture")
        return False
    if not message.reply_to_message.photo:
        bot_instance.reply_to(message, "Где картинка сука")
        return False
    return True

def download_img_from_telegram(message: telebot.types.Message) -> bytearray:
    fileID = message.photo[-1].file_id
    file_info = bot_instance.get_file(fileID)
    return bot_instance.download_file(file_info.file_path)

@bot_instance.message_handler(commands=['ping'])
def handle_ping(message: telebot.types.Message):
    bot_instance.reply_to(message, "Alive")

@bot_instance.message_handler(commands=['get_rtf'])
def handle_rtf(message: telebot.types.Message):
    rtf_chanell_id = -1001632815403
    rtf_mes_count = 15358
    while True:
        try:
            msg_id = random.randint(0, rtf_mes_count)
            bot_instance.forward_message(message.chat.id, rtf_chanell_id, msg_id)
            break
        except Exception as e:
            print(e)


@bot_instance.message_handler(commands=['get_random_chat_msg'])
def get_random_chat_msg(message: telebot.types.Message):
    chat_id = message.chat.id
    current_try = MAX_TRIES
    while current_try > 0:
        current_try -= 1
        try:
            msg_id = np.random.choice(message.id)
            fwd = bot_instance.forward_message(chat_id=chat_id, from_chat_id=chat_id, message_id=msg_id)
            bot_instance.reply_to(message=fwd, text=f"Link: https://t.me/c/{normalize_tg_chat_id(chat_id)}/{msg_id}")
            break
        except Exception as e:
            pass

@bot_instance.message_handler(commands=['get_count'])
def handle_image_count(message: telebot.types.Message):
    bot_instance.reply_to(message, db_service.get_images_count(str(message.chat.id)))

def is_message_existing(chat_id, msg_id):
    try:
        bot_instance.copy_message(chat_id=DUMP_CHANNEL_ID, from_chat_id=chat_id, message_id=msg_id)
        return True
    except Exception as e:
        return False
