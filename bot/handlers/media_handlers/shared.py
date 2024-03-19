
from bot.handlers.shared import normalize_tg_chat_id
from services.db_service import DbService
import math
import telebot

db_service = DbService()
MAX_RATING = 5.0

def update_drating(duplicates, chatId, userId):
    rating = 0.0
    for dup in duplicates:
        dist = dup["dist"]
        rating += get_rating(dist)
        
    chatId = normalize_tg_chat_id(chatId)    
    db_service.update_drating(str(chatId), userId, rating)
        
def get_rating(dist):
    return round(MAX_RATING * math.exp(-dist/5.0), 2)

def get_chat_member_safe(bot_instance: telebot.TeleBot, message: telebot.types.Message, rating):
    try:
        return bot_instance.get_chat_member(message.chat.id, rating.userId).user.full_name
    except:
        return ""