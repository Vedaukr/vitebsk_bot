from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import normalize_tg_chat_id, tg_exception_handler
import telebot
from services.db_service import DbService

db_service = DbService()

@bot_instance.message_handler(commands=['get_dementia_rating'])
@tg_exception_handler
def get_dem_rating(message: telebot.types.Message):
    chat_id = message.chat.id
    if chat_id < 0:
        chat_id = normalize_tg_chat_id(chat_id)
    
    ratings = db_service.get_sorted_drating(str(chat_id))
    
    if not ratings:
        bot_instance.reply_to(message, "Retard count is zero for now.")
        return

    response = "🌹😔 DEMENTIA RATING: 😔🌹\n"

    for index, rating in enumerate(ratings):
        try:
            chat_user = bot_instance.get_chat_member(message.chat.id, rating.userId)
        except Exception as e:
            response += f"{index+1}. {rating.userId} | {round(rating.rating, 2)} \n"
            continue
        response += f"{index+1}. {chat_user.user.full_name} | {round(rating.rating, 2)} \n"
    
    bot_instance.reply_to(message, response)