from import_bot import bot_instance
from settings import settings

AUTH_CHAT_ID = settings['AUTH_CHAT_ID']
if __name__ == "__main__":
    bot_instance.send_message(AUTH_CHAT_ID, "[DEBUG] Bot restarted.")
    bot_instance.infinity_polling()