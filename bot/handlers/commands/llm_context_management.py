import logging
from bot.bot_instance.bot import bot_instance
import telebot
from bot.handlers.shared import get_tg_link, tg_exception_handler
from services.llm.llm_user_context import LlmUserContext
from services.llm.models.llm_message import LlmMessageRole, LlmMessageType
from utils.md_utils import escape_markdown, get_md_link

global_llm_context = LlmUserContext()
logger = logging.getLogger(__name__)

@bot_instance.message_handler(commands=['clear_llm_context'])
@tg_exception_handler
def clr_handler(message: telebot.types.Message):
    global_llm_context.reset_user_context(str(message.from_user.id))
    bot_instance.reply_to(message, "Context cleared.")

@bot_instance.message_handler(commands=['get_llm_context'])
@tg_exception_handler
def get_ctx_handler(message: telebot.types.Message):
    user_context = global_llm_context.get_user_context(str(message.from_user.id))
    if not user_context:
        bot_instance.reply_to(message, "Context is empty.")
        return

    bot_response = ""
    for msg in user_context:
        if msg.type == LlmMessageType.TEXT:
            role = "user" if msg.role == LlmMessageRole.USER else msg.metadata.get('model_name') or "no model idk"
            msg_id = msg.metadata.get("msg_id")
            msg_link = get_md_link('LINK', get_tg_link(message.chat.id, msg_id)) if msg_id else ""
            bot_response += f"\n{escape_markdown(msg.content[:20])} \.\.\. \| {msg_link} \| {escape_markdown(role)}"

    try:
        bot_instance.reply_to(message, bot_response, parse_mode="MarkdownV2")
    except Exception as ex:
        logger.error(f"Markdown error: {ex}.\nMessage in question:\n{bot_response}")
        bot_instance.reply_to(message, bot_response)
    