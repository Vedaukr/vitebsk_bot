from bot.bot_instance.bot import bot_instance
from services.db_service import DbService
from services.duplication_service import DuplicationService

# Singletones
dup_service = DuplicationService()
db_service = DbService()

@bot_instance.callback_query_handler(func=lambda call: True)
def command_handler(call):
    qtype, chat_id, msg_id = call.data.split('|')
    bot_msg_id = call.message.message_id
    bot_instance.delete_message(chat_id, bot_msg_id)
    media_info = dup_service.get_media(chat_id, msg_id)
    dup_service.delete_media(media_info)

    if qtype == 'r':
        bot_instance.delete_message(chat_id, msg_id)

    if qtype == 'f' and media_info:
        db_service.save_media_to_db(media_info)