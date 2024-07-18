from bot.bot_instance.bot import bot_instance
from bot.handlers.msg_handlers.shared import get_prompt
from bot.handlers.shared import tg_exception_handler, continue_handling, msg_starts_with_filter, get_msg_text
from services.openai_service import OpenAiService
import telebot
import base64

from utils.md_utils import escape_markdown   

param_info = {
    "max_tokens": """The maximum number of tokens that can be generated in the chat completion.
The total length of input tokens and generated tokens is limited by the model's context length.""",
    "presence_penalty": "Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.",
    "frequency_penalty": "Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.",
    "temperature": "What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic",
}

# Singletons
openai_service = OpenAiService()

@bot_instance.message_handler(func=msg_starts_with_filter(("gpt ", "гпт ")), content_types=['text', 'photo'])
@tg_exception_handler
@continue_handling
def gpt_handler(message: telebot.types.Message):
    bot_reply = bot_instance.reply_to(message, "generating...")    
    base64_image, img_ext = try_get_image(message)  
    msg_text = get_msg_text(message)
    prompt = get_prompt(msg_text)
    openai_response = openai_service.generate_text(prompt, model_name="gpt-4o-mini", user_id=str(message.from_user.id), base64_image=base64_image, img_ext=img_ext)
    try:
        bot_instance.edit_message_text(escape_markdown(openai_response, entity_type='code'), message.chat.id, bot_reply.message_id, parse_mode="MarkdownV2")
    except Exception:
        bot_instance.edit_message_text(openai_response, message.chat.id, bot_reply.message_id)


@bot_instance.message_handler(func=msg_starts_with_filter(("gpt4 ", "гпт4 ")), content_types=['text', 'photo'])
@tg_exception_handler
@continue_handling
def gpt4_handler(message: telebot.types.Message):
    bot_reply = bot_instance.reply_to(message, "generating...")  
    base64_image, img_ext = try_get_image(message)  
    msg_text = get_msg_text(message)
    prompt = get_prompt(msg_text)
    openai_response = openai_service.generate_text(prompt, model_name="gpt-4o", user_id=str(message.from_user.id), base64_image=base64_image, img_ext=img_ext)
    try:
        bot_instance.edit_message_text(escape_markdown(openai_response, entity_type='code'), message.chat.id, bot_reply.message_id, parse_mode="MarkdownV2")
    except Exception:
        bot_instance.edit_message_text(openai_response, message.chat.id, bot_reply.message_id)

@bot_instance.message_handler(commands=["get_gpt_params"])
@tg_exception_handler
def get_params_handler(message: telebot.types.Message):
    response = "GPT params:\n\n"
    for k, v in openai_service.params.items():
        response += f"{k} = {v}\n{param_info[k]}\n\n"
    response += "set_gpt_param param_name value"
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

def try_get_image(message: telebot.types.Message) -> tuple[str, str]:
    if message.photo:
        return get_photo_base64(message.photo[-1].file_id)
    
    if message.reply_to_message and message.reply_to_message.photo:
        return get_photo_base64(message.reply_to_message.photo[-1].file_id)
    
    return (None, None)
        
def get_photo_base64(fileId: str) -> tuple[str, str]:
    file_info = bot_instance.get_file(fileId)
    img_bytes = bot_instance.download_file(file_info.file_path)
    return base64.b64encode(img_bytes).decode('utf-8'), file_info.file_path.split('.')[-1]