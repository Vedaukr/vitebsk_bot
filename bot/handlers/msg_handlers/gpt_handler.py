from bot.bot_instance.bot import bot_instance
from bot.handlers.msg_handlers.shared import get_prompt
from bot.handlers.shared import tg_exception_handler, continue_handling, msg_starts_with_filter, get_msg_text, try_get_image
from services.openai_service import OpenAiService
import telebot
import base64
import logging

from utils.lev_distance_util import find_closest_word
from utils.md_utils import escape_markdown   

param_info = {
    "max_tokens": """The maximum number of tokens that can be generated in the chat completion.
The total length of input tokens and generated tokens is limited by the model's context length.""",
    "presence_penalty": "Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.",
    "frequency_penalty": "Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.",
    "temperature": "What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic",
}

# gotta be better way to do this i guess
default_gpt_model_mapping = {
    "gpt": "gpt-4o-mini",
    "гпт": "gpt-4o-mini",
    "gpt4": "gpt-4o",
    "гпт4": "gpt-4o",
    "o1": "o1-mini"
}

bot_triggers = ("gpt", "гпт", "o1")

# Singletons
openai_service = OpenAiService()
logger = logging.getLogger(__name__)

@bot_instance.message_handler(func=msg_starts_with_filter(bot_triggers), content_types=['text', 'photo'])
@tg_exception_handler
@continue_handling
def gpt_handler(message: telebot.types.Message):
    base64_image, img_ext = try_get_image(message)
    msg_text = get_msg_text(message)

    model_name, is_exact_match = get_model_name(msg_text)
    if not is_exact_match:
        bot_instance.reply_to(message, f"Model with name {msg_text.split()[0].lower()} was not found, using {model_name} instead.")    

    bot_reply = bot_instance.reply_to(message, "generating...")    
    prompt = get_prompt(msg_text)
    openai_response = openai_service.generate_text(prompt, model_name=model_name, user_id=str(message.from_user.id), base64_image=base64_image, img_ext=img_ext)
    try:
        bot_instance.edit_message_text(escape_markdown(openai_response, entity_type='code'), message.chat.id, bot_reply.message_id, parse_mode="MarkdownV2")
    except Exception as ex:
        logger.error(f"Markdown error: {ex}.\nMessage in question:\n{openai_response}")
        bot_instance.edit_message_text(openai_response, message.chat.id, bot_reply.message_id)

@bot_instance.message_handler(commands=["get_gpt_params"])
@tg_exception_handler
def get_params_handler(message: telebot.types.Message):
    response = "GPT params:\n\n"
    for k, v in openai_service.params.items():
        response += f"{k} = {v}\n{param_info[k]}\n\n"
    response += "set_gpt_param param_name value"
    bot_instance.reply_to(message, response)

@bot_instance.message_handler(commands=["get_available_openai_models"])
@tg_exception_handler
def get_available_openai_models(message: telebot.types.Message):
    response = "Available models:\n\n"
    for model in openai_service.get_available_models_info():
        if model.startswith(bot_triggers):
            response += f"{model}\n"
    bot_instance.reply_to(message, response)

@bot_instance.message_handler(commands=["reset_gpt_params"])
@tg_exception_handler
def reset_params_handler(message: telebot.types.Message):
    openai_service.reset_defaults()
    bot_instance.reply_to(message, "Reset suckassfull.")    

@bot_instance.message_handler(regexp=r"^(\bset_gpt_param\b)\s.+")
@tg_exception_handler
def set_params_handler(message: telebot.types.Message):
    prompt = get_prompt(message.text)
    param, value = prompt.split(" ")[0], prompt.split(" ")[1]
    if not param in openai_service.params:
        bot_instance.reply_to(message, "Invalid param name")
        return
    
    try:
        num_value = float(value)
    except Exception as e:
        bot_instance.reply_to(message, "Error on conversion value to number.")
        return
    
    openai_service.params[param] = num_value
    bot_instance.reply_to(message, f"Param {param} set to {num_value}. If value is outside of supposed range go fuck yourself.")

# Returns model_name and flag if exact model name is available
def get_model_name(message: str) -> tuple[str, bool]:
    trigger = message.split(" ")[0].lower()
    if trigger in default_gpt_model_mapping:
        return default_gpt_model_mapping[trigger], True
    
    model_name, dist = find_closest_word(trigger, openai_service.get_available_models_info())
    return model_name, dist == 0