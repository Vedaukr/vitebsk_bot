import telebot, os
from import_bot import bot_instance
from import_bot import bot_token
from flask import Flask, request

host = os.environ["BOT_HOST"]
server = Flask(__name__) 

try:
    bot_instance.set_webhook(url=f'{host}/{bot_token}')
except Exception as e:
    bot_instance.remove_webhook()
    bot_instance.set_webhook(url=f'{host}/{bot_token}')

@server.route(f'/{bot_token}', methods=['POST'])
def getMessage():
    print("Got new request from telegram")
    bot_instance.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)