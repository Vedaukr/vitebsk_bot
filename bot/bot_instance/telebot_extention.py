import types
import telebot

TELEGRAM_MAX_MESSAGE_LENGTH = 4096
MSG_TEXT_ARGUMENT = "text"

def split_msgs(func):
    def wrapper(*args, **kwargs):
        if not MSG_TEXT_ARGUMENT in kwargs:
            return func(*args, **kwargs)
        text = kwargs[MSG_TEXT_ARGUMENT]
        msgs = [text[i:i + TELEGRAM_MAX_MESSAGE_LENGTH] for i in range(0, len(text), TELEGRAM_MAX_MESSAGE_LENGTH)]
        for msg in msgs:
            try:
                kwargs[MSG_TEXT_ARGUMENT] = msg
                res = func(*args, **kwargs)
            except Exception:
                pass
        return res
    return wrapper

class TelebotExt(telebot.TeleBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @split_msgs
    def edit_message_text(self, *args, **kwargs): 
        return super().edit_message_text(*args, **kwargs)

    @split_msgs    
    def send_message(self, *args, **kwargs):
        return super().send_message(*args, **kwargs)
    
    @split_msgs
    def reply_to(self, *args, **kwargs):
        return super().reply_to(*args, **kwargs)