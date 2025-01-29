import json

import requests
from bot.bot_instance.bot import bot_instance
from bot.handlers.msg_handlers.shared import get_prompt
from bot.handlers.configs.llm_config import default_model_mapping
from bot.handlers.shared import tg_exception_handler, continue_handling, msg_starts_with_filter, get_msg_text, try_get_image
import telebot
import logging

from services.llm.llm_user_context import LlmUserContext
from services.llm.models.llm_message import LlmMessage, LlmMessageRole, LlmMessageType
from services.llm.models.llm_reponse import LlmResponse
from settings import TELEGRAPH_TOKEN
from utils.md_utils import escape_markdown, get_md_link   

MAX_CTX_SIZE = 10

# Singletons
logger = logging.getLogger(__name__)
global_llm_context = LlmUserContext()

@bot_instance.message_handler(func=lambda message: message.reply_to_message is not None, content_types=['text'])
@tg_exception_handler
def llm_reply_handler(message: telebot.types.Message):
    user_id = str(message.from_user.id)
    user_context = global_llm_context.get_user_context(user_id)
    if user_context:
        msgs = [msg for msg in user_context if msg.metadata.get('msg_id') is not None]
        if str(message.reply_to_message.message_id) in [msg.metadata.get('msg_id') for msg in msgs]:
            llm_msg = next(msg for msg in msgs[::-1] if msg.role == LlmMessageRole.LLM)
            if model_name := llm_msg.metadata.get('model_name'):
                handle_llm_call(message, model_name, prompt=get_msg_text(message))
                return

    return telebot.ContinueHandling()


@bot_instance.message_handler(func=msg_starts_with_filter(tuple(default_model_mapping.keys())), content_types=['text', 'photo'])
@tg_exception_handler
@continue_handling
def llm_handler(message: telebot.types.Message):
    msg_text = get_msg_text(message)   
    prompt = get_prompt(msg_text)
    model_name = msg_text.split()[0].lower()
    handle_llm_call(message, model_name, prompt)

def handle_llm_call(message: telebot.types.Message, model_name: str, prompt: str):    
    base64_image, img_ext = try_get_image(message)

    llm_model = default_model_mapping.get(model_name)
    if not llm_model:
        bot_instance.reply_to(message, f"Unrecognized model name {model_name}.")
        return 

    bot_reply = bot_instance.reply_to(message, "generating...") 
    user_id = str(message.from_user.id)
    user_context = global_llm_context.get_user_context(user_id)
    llm_response = llm_model.generate_text(prompt, user_context=user_context[-MAX_CTX_SIZE:], img=base64_image, img_ext=img_ext)
    output = llm_response.content
        
    user_context.append(LlmMessage(role=LlmMessageRole.USER, type=LlmMessageType.TEXT, content=prompt, metadata={'msg_id': str(message.id)}))
    user_context.append(LlmMessage(role=LlmMessageRole.LLM, type=LlmMessageType.TEXT, content=output, metadata={'model_name': model_name, 'msg_id': str(bot_reply.id)}))
    
    llm_meta_appendix = get_llm_meta_appendix(llm_model.model_name, llm_response)
    
    try:
        formatted_output = f"{escape_markdown(output, entity_type='code')}{llm_meta_appendix}"
        bot_instance.edit_message_text(formatted_output, message.chat.id, bot_reply.message_id, parse_mode="MarkdownV2")
    except Exception as ex:
        logger.error(f"Markdown error: {ex}.\nMessage in question:\n{output}")
        formatted_output = f"{output}{llm_meta_appendix}"
        bot_instance.edit_message_text(formatted_output, message.chat.id, bot_reply.message_id)

def get_llm_meta_appendix(model_name: str, llm_response: LlmResponse) -> str:
    result = f"\n\n\-\-\-\n\[LLM meta\] Model used: {escape_markdown(model_name)}"

    if total_tokens := llm_response.metadata.get("total_tokens"):
        result += f"\n\[LLM meta\] Token usage: {total_tokens}"
    
    if reasoning := llm_response.metadata.get("reasoning"):
        telegraph_url = post_to_telegraph(reasoning)
        result += f"\n\[LLM meta\] {get_md_link('Reasoning', telegraph_url)}" if telegraph_url else "\n\nUnable to create telegraph article, see logs."

    return result

def post_to_telegraph(reasoning: str) -> str:
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
                'title': f'DS-REASONING-{reasoning[:15]}',
                'content': json.dumps(content, ensure_ascii=False),
                'author_name': "DS-vbot"
            }
        )
        page_response.raise_for_status()
        return page_response.json()['result']['url']
    except requests.RequestException as e:
        logger.error(f"Request error when trying to post reasoning to telegraph: {e}. Response: {page_response.json()}")
        return ""