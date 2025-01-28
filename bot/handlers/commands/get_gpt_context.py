from bot.bot_instance.bot import bot_instance
from bot.handlers.shared import tg_exception_handler
import telebot
from services.llm.openai_service import OpenAiService

openai_service = OpenAiService()

@bot_instance.message_handler(commands=['get_gpt_context'])
@tg_exception_handler
def get_ctx_handler(message: telebot.types.Message):
    ctx = openai_service.get_or_create_context(str(message.from_user.id))
    ctx_str = openai_service.convert_context_to_str(ctx)
    bot_instance.reply_to(message, f"Your context:\n{ctx_str if ctx else 'empty context'}")