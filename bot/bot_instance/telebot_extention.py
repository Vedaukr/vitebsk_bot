from typing import Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter
import telebot

TELEGRAM_MAX_MESSAGE_LENGTH = 4096

def send_message_in_reply_chain(
    bot_instance: telebot.TeleBot,
    chat_id: int,
    message: str,
    reply_message: Optional[telebot.types.Message] = None,
    *args,
    **kwargs
) -> telebot.types.Message:
    """
    Send messages in reply chain to the message.
    """
    
    if len(message) <= TELEGRAM_MAX_MESSAGE_LENGTH:
        reply_id = reply_message.message_id if reply_message else None
        return bot_instance.send_message(chat_id, message, reply_to_message_id=reply_id, *args, **kwargs)
    
    messages = RecursiveCharacterTextSplitter(
            chunk_size=TELEGRAM_MAX_MESSAGE_LENGTH,
            chunk_overlap=0 
        ).split_text(message)

    for msg in messages:
        reply_id = reply_message.message_id if reply_message else None
        reply_message = bot_instance.send_message(chat_id, msg, reply_to_message_id=reply_id, *args, **kwargs)
    
    return reply_message