from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import download_img_from_telegram
from bot.handlers.shared import tg_exception_handler
from services.labeling_service import LabelingService
import telebot

label_service = LabelingService()

@bot_instance.message_handler(commands=['get_img_labels'])
@tg_exception_handler
def handle_labels(message: telebot.types.Message):
    if handle_img_request(message):
        img_bytes = download_img_from_telegram(message.reply_to_message)
        labels = label_service.get_labels(img_bytes)
        lab_msg = "\n".join(labels)
        msg = f"Labels:\n{ lab_msg }"
        bot_instance.reply_to(message, msg)

@bot_instance.message_handler(commands=['get_img_text'])
@tg_exception_handler
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
