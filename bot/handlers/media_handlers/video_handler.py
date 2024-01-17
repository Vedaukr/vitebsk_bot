import telebot
from services.duplication_service import DuplicationService
from services.db_service import DbService
from services.shared import MediaInfo
from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import create_message, get_keyboard, normalize_tg_chat_id
from bot.handlers.shared import tg_exception_handler
from .shared import update_drating

# Singletones
dup_service = DuplicationService()
db_service = DbService()

@bot_instance.message_handler(content_types=['video'])
@tg_exception_handler
def handle_video(message: telebot.types.Message):

    fileID = message.video.file_id
    file_info = bot_instance.get_file(fileID)

    media_info = MediaInfo(
        msg_id=str(message.message_id),
        author_id=str(message.from_user.id),
        chat_id=str(message.chat.id),
        media_bytes=bot_instance.download_file(file_info.file_path),
        media_type="video",
    )

    duplicates = dup_service.detect_media_duplicates(media_info)

    if (duplicates):
        user_id = message.from_user.id
    
        if message.forward_signature:
            ratings = db_service.get_sorted_drating(normalize_tg_chat_id(message.chat.id))
            usernames = list(map(lambda r: (r.userId, bot_instance.get_chat_member(message.chat.id, r.userId).user.full_name), ratings))
            for uname in usernames:
                if message.forward_signature == uname[1]:
                    user_id = uname[0]
                    break

        update_drating(duplicates, chatId=message.chat.id, userId=str(user_id))
        reply_msg = create_message(duplicates, message.chat.id)
        reply_markup = get_keyboard(media_info.chat_id, message.message_id)
        bot_instance.reply_to(message, reply_msg, reply_markup=reply_markup)
    else:
        db_service.save_media_to_db(media_info)
        dup_service.delete_media(media_info)
