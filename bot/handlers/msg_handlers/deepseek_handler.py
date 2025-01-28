import json
import requests
from bot.bot_instance.bot import bot_instance
from bot.handlers.msg_handlers.shared import get_prompt
from bot.handlers.shared import tg_exception_handler, continue_handling, msg_starts_with_filter, get_msg_text, try_get_image
import telebot
import logging

from services.llm.deepseek_service import DeepseekService
from settings import TELEGRAPH_TOKEN
from utils.md_utils import escape_markdown, get_md_link   

bot_triggers = ("deepseek", "ds", "dsr")

default_model_mapping = {
    "ds": "deepseek-chat",
    "dsr": "deepseek-reasoner",
    "deepseek": "deepseek-reasoner"
}

# Singletons
ds_service = DeepseekService()
logger = logging.getLogger(__name__)

@bot_instance.message_handler(func=msg_starts_with_filter(bot_triggers), content_types=['text', 'photo'])
@tg_exception_handler
@continue_handling
def deepseek_handler(message: telebot.types.Message):
    msg_text = get_msg_text(message)
    bot_reply = bot_instance.reply_to(message, "generating...")    
    prompt = get_prompt(msg_text)
    
    model_name = default_model_mapping.get(msg_text.split()[0].lower(), "deepseek-chat")
    ds_response, ds_reasoning = ds_service.generate_text(prompt, user_id=str(message.from_user.id), model_name=model_name)
    ds_response = escape_markdown(ds_response, entity_type='code')
    if ds_reasoning:
        telegraph_url = post_to_telegraph(prompt, ds_reasoning)
        ds_response += f"\n\n\(Deepseek meta\) {get_md_link('Reasoning', telegraph_url)}" if telegraph_url else "\n\nUnable to create telegraph article, see logs."
    
    try:
        bot_instance.edit_message_text(ds_response, message.chat.id, bot_reply.message_id, parse_mode="MarkdownV2")
    except Exception as ex:
        logger.error(f"Markdown error: {ex}.\nMessage in question:\n{ds_response}")
        bot_instance.edit_message_text(ds_response, message.chat.id, bot_reply.message_id)

def post_to_telegraph(prompt: str, reasoning: str) -> str:
    content = [
        {
            "tag": "p",
            "children": [line]
        }
        for line in reasoning.split('\n') if line
    ]

    try:
        page_response = requests.post(
            'https://api.telegra.ph/createPage',
            data={
                'access_token': TELEGRAPH_TOKEN,
                'title': f'DS-REASONING-{prompt[:15]}',
                'content': json.dumps(content, ensure_ascii=False),
                'author_name': "DS-vbot"
            }
        )
        page_response.raise_for_status()
        return page_response.json()['result']['url']
    except requests.RequestException as e:
        logger.error(f"Request error when trying to post reasoning to telegraph: {e}. Response: {page_response.json()}")
        return ""