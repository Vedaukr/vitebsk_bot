from bot.bot_instance.bot import bot_instance
from bot.handlers.msg_handlers.shared import get_prompt
from bot.handlers.shared import tg_exception_handler, continue_handling, msg_starts_with_filter, get_msg_text, try_get_image
from services.llm.anthropic_service import AnthropicService
import telebot
import logging

from utils.md_utils import escape_markdown   

bot_triggers = ("claude", "haiku", "sonnet", "opus")

default_model_mapping = {
    "claude": "claude-3-5-sonnet-latest",
    "haiku": "claude-3-5-haiku-latest",
    "sonnet": "claude-3-5-sonnet-latest",
    "opus": "claude-3-opus-latest"
}

# Singletons
anth_service = AnthropicService()
logger = logging.getLogger(__name__)

@bot_instance.message_handler(func=msg_starts_with_filter(bot_triggers), content_types=['text', 'photo'])
@tg_exception_handler
@continue_handling
def gpt_handler(message: telebot.types.Message):
    base64_image, img_ext = try_get_image(message)
    msg_text = get_msg_text(message)

    model_name = default_model_mapping.get(msg_text.split()[0].lower(), "claude-3-5-sonnet-latest")

    bot_reply = bot_instance.reply_to(message, "generating...")    
    prompt = get_prompt(msg_text)
    anth_response = anth_service.generate_text(prompt, model_name=model_name, user_id=str(message.from_user.id), base64_image=base64_image)
    try:
        bot_instance.edit_message_text(escape_markdown(anth_response, entity_type='code'), message.chat.id, bot_reply.message_id, parse_mode="MarkdownV2")
    except Exception as ex:
        logger.error(f"Markdown error: {ex}.\nMessage in question:\n{anth_response}")
        bot_instance.edit_message_text(anth_response, message.chat.id, bot_reply.message_id)