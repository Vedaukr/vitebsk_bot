import json
from typing import Any

import requests
from bot.bot_instance.bot import bot_instance
from bot.handlers.msg_handlers.shared import get_prompt
from bot.handlers.shared import tg_exception_handler, continue_handling, msg_starts_with_filter, get_msg_text, try_get_image
import telebot
import logging

from services.llm.deepseek_llm import DeepseekLlm
from services.llm.llm_model import LlmModel
from services.llm.models.llm_reponse import LlmResponse
from services.llm.openai_llm import OpenAiLlm, OpenAiO1Llm
from services.llm.anthropic_llm import AnthropicLlm
from settings import TELEGRAPH_TOKEN
from utils.md_utils import escape_markdown, get_md_link   

# Singletons
logger = logging.getLogger(__name__)

default_model_mapping: dict[str, LlmModel] = {}

# openai
default_model_mapping["gpt"] = OpenAiLlm(model_name="gpt-4o-mini") 
default_model_mapping["гпт"] = OpenAiLlm(model_name="gpt-4o-mini") 
default_model_mapping["gpt4"] = OpenAiLlm(model_name="gpt-4o") 
default_model_mapping["гпт4"] = OpenAiLlm(model_name="gpt-4o") 
default_model_mapping["o1"] = OpenAiO1Llm(model_name="o1-mini") 
default_model_mapping["o1p"] = OpenAiO1Llm(model_name="o1-preview")

# anthropic
default_model_mapping["anth"] = AnthropicLlm(model_name="claude-3-5-sonnet-latest") 
default_model_mapping["claude"] = AnthropicLlm(model_name="claude-3-5-sonnet-latest") 
default_model_mapping["haiku"] = AnthropicLlm(model_name="claude-3-5-haiku-latest") 
default_model_mapping["sonnet"] = AnthropicLlm(model_name="claude-3-5-sonnet-latest") 
default_model_mapping["opus"] = AnthropicLlm(model_name="claude-3-opus-latest", is_vision_model=False)

# deepseek
default_model_mapping["ds"] = DeepseekLlm(model_name="deepseek-chat", is_vision_model=False) 
default_model_mapping["dsr"] = DeepseekLlm(model_name="deepseek-reasoner", is_vision_model=False) 
default_model_mapping["deepseek"] = DeepseekLlm(model_name="deepseek-reasoner", is_vision_model=False)

@bot_instance.message_handler(func=msg_starts_with_filter(tuple(default_model_mapping.keys())), content_types=['text', 'photo'])
@tg_exception_handler
@continue_handling
def gpt_handler(message: telebot.types.Message):
    base64_image, img_ext = try_get_image(message)
    msg_text = get_msg_text(message)   
    prompt = get_prompt(msg_text)

    model_name = msg_text.split()[0].lower()
    llm_model = default_model_mapping.get(model_name)
    if not llm_model:
        bot_instance.reply_to(message, f"Unrecognized model name {model_name}.")
        return 

    bot_reply = bot_instance.reply_to(message, "generating...") 
    llm_response = llm_model.generate_text(prompt, img=base64_image, img_ext=img_ext)
    output = llm_response.content
    llm_meta_appendix = get_llm_meta_appendix(llm_response)
    
    try:
        formatted_output = f"{escape_markdown(output, entity_type='code')}{llm_meta_appendix}"
        bot_instance.edit_message_text(formatted_output, message.chat.id, bot_reply.message_id, parse_mode="MarkdownV2")
    except Exception as ex:
        logger.error(f"Markdown error: {ex}.\nMessage in question:\n{output}")
        formatted_output = f"{output}{llm_meta_appendix}"
        bot_instance.edit_message_text(output, message.chat.id, bot_reply.message_id)

def get_llm_meta_appendix(llm_response: LlmResponse) -> str:
    result = ""
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