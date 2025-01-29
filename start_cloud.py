import telebot, os
from import_bot import bot_instance
from flask import Flask, request
from settings import BOT_NAME
import logging

from settings.base import AUTH_CHAT_ID


host = os.environ["BOT_HOST"]
server = Flask(__name__)
logger = logging.getLogger(__name__)

try:
    bot_instance.set_webhook(url=f'{host}/{BOT_NAME}')
except Exception as e:
    logger.error(e.with_traceback(None))
    bot_instance.remove_webhook()
    bot_instance.set_webhook(url=f'{host}/{BOT_NAME}')

@server.route(f'/{BOT_NAME}', methods=['POST'])
def getMessage():
    bot_instance.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

def check_if_restarted_by_oom() -> bool:
    return os.environ.get('LAST_EXIT_CODE') == '137'

if __name__ == "__main__":
    start_message = "Bot restarted on OOM." if check_if_restarted_by_oom() else "Bot restarted."
    bot_instance.send_message(AUTH_CHAT_ID, f"[DEBUG] {start_message}")
    server.run(host="0.0.0.0", port=8080)