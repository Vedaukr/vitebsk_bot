from bot.bot_instance.bot import bot_instance
from services.openai_service import OpenAiService
import telebot

# Singletones
openai_service = OpenAiService()

@bot_instance.message_handler(regexp=r"^(\bgpt\b|\bгпт\b)\s.+")
def msg_handler(message: telebot.types.Message):
    bot_reply = bot_instance.reply_to(message, "generating...")
    prompt = " ".join(message.text.split(" ")[1:])
    openai_response = openai_service.get_response(prompt)
    bot_instance.edit_message_text(openai_response, message.chat.id, bot_reply.message_id)

@bot_instance.message_handler(commands=['clear_context'])
def clr_handler(message: telebot.types.Message):
    openai_service.clear_context()
    bot_instance.reply_to(message, "Context cleared.")