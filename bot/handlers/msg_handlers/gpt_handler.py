from bot.bot_instance.bot import bot_instance
from bot.handlers.msg_handlers.shared import get_prompt
from bot.handlers.shared import tg_exception_handler
from services.openai_service import OpenAiService
import telebot

param_info = {
    "max_tokens": """The maximum number of tokens that can be generated in the chat completion.
The total length of input tokens and generated tokens is limited by the model's context length.""",
    "presence_penalty": "Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.",
    "frequency_penalty": "Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.",
    "temperature": "What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic",
}

# Singletons
openai_service = OpenAiService()

@bot_instance.message_handler(regexp=r"^(\bgpt\b|\bгпт\b)\s.+")
@tg_exception_handler
def msg_handler(message: telebot.types.Message):
    bot_reply = bot_instance.reply_to(message, "generating...")    
    prompt = get_prompt(message.text)
    openai_response = openai_service.get_response(prompt, model_name="gpt-3.5-turbo", user_id=str(message.from_user.id))
    bot_instance.edit_message_text(openai_response, message.chat.id, bot_reply.message_id)

@bot_instance.message_handler(regexp=r"^(\bgpt4\b|\bгпт4\b)\s.+")
@tg_exception_handler
def msg_handler(message: telebot.types.Message):
    bot_reply = bot_instance.reply_to(message, "generating...")    
    prompt = get_prompt(message.text)
    openai_response = openai_service.get_response(prompt, model_name="gpt-4", user_id=str(message.from_user.id))
    bot_instance.edit_message_text(openai_response, message.chat.id, bot_reply.message_id)

@bot_instance.message_handler(commands=["get_gpt_params"])
@tg_exception_handler
def msg_handler(message: telebot.types.Message):
    response = "GPT params:\n\n"
    for k, v in openai_service.params.items():
        response += f"{k} = {v}\n{param_info[k]}\n\n"
    response += "set_gpt_param param_name value"
    bot_instance.reply_to(message, response)

@bot_instance.message_handler(commands=["reset_gpt_params"])
@tg_exception_handler
def msg_handler(message: telebot.types.Message):
    openai_service.reset_defaults()
    bot_instance.reply_to(message, "Reset suckassfull.")    

@bot_instance.message_handler(regexp=r"^(\bset_gpt_param\b)\s.+")
@tg_exception_handler
def msg_handler(message: telebot.types.Message):
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
