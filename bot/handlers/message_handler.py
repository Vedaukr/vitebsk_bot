from bot.bot_instance.bot import bot_instance
from services.openai_service import OpenAiService
from services.search_service import SearchService
from utils.search_resolver import search_resolver
import telebot

PICTURE_TRIGGERS = ("картинка", "пикча", "image", "img", "picture")

# Singletons
openai_service = OpenAiService()
search_service = SearchService()

@bot_instance.message_handler(regexp=r"^(\bgpt\b|\bгпт\b)\s.+")
def msg_handler(message: telebot.types.Message):
    try:
        bot_reply = bot_instance.reply_to(message, "generating...")    
        prompt = get_prompt(message.text)
        openai_response = openai_service.get_response(prompt, str(message.from_user.id))
        bot_instance.edit_message_text(openai_response, message.chat.id, bot_reply.message_id)
    except Exception as e:
        print(str(e.with_traceback(None)))
        bot_instance.reply_to(message, f"Something fucked up: {str(e.with_traceback(None))}")

@bot_instance.message_handler(regexp=r"^(\bbot\b|\bбот\b)\s.+")
def img_handler(message: telebot.types.Message):
    try:
        prompt = get_prompt(message.text)
        if prompt.startswith(PICTURE_TRIGGERS):
                picture_prompt = get_prompt(prompt)
                if picture_prompt:
                    bot_reply = bot_instance.reply_to(message, "searching...")
                    img_link = search_service.get_image(picture_prompt)
                    bot_instance.delete_message(bot_reply.chat.id, bot_reply.message_id)
                    bot_instance.send_photo(message.chat.id, img_link, caption=picture_prompt, reply_to_message_id=message.message_id)

        search_handler = search_resolver.get_site_search_handler(prompt=prompt)
        if search_handler:
            search_prompt = get_prompt(prompt)
            if search_prompt:
                bot_reply = bot_instance.reply_to(message, "searching...")
                links = search_service.get_search_results(search_prompt, search_handler.get_site_uri())
                response = search_handler.get_response(links)
                bot_instance.edit_message_text(response, message.chat.id, bot_reply.message_id, parse_mode="MarkdownV2")

    except Exception as e:
        print(str(e.with_traceback(None)))
        bot_instance.reply_to(message, f"Something fucked up: {str(e.with_traceback(None))}")

@bot_instance.message_handler(commands=['clear_gpt_context'])
def clr_handler(message: telebot.types.Message):
    openai_service.clear_context(str(message.from_user.id))
    bot_instance.reply_to(message, "Context cleared.")

@bot_instance.message_handler(commands=['get_gpt_context'])
def get_ctx_handler(message: telebot.types.Message):
    ctx = openai_service.get_or_create_context(str(message.from_user.id))
    bot_instance.reply_to(message, f"Your context:\n{ctx if ctx else 'empty ctx'}")

@bot_instance.message_handler(commands=['get_bot_triggers'])
def get_bot_triggers(message: telebot.types.Message):
    response = f"Usage: bot [trigger] [trigger_prompt]\n\n"
    response += f"Picture triggers: {PICTURE_TRIGGERS}\n\n"
    response += "Search triggers:\n"
    for handler in search_resolver.handlers:
        uri = handler.get_site_uri()
        response += f"Site: {uri if uri else 'Default search'}, Triggers: {handler.get_triggers()}\n"
    bot_instance.reply_to(message, response)

def get_prompt(bot_request):
    return " ".join(str.lower(bot_request).split(" ")[1:])