from bot.bot_instance.bot import bot_instance
from services.openai_service import OpenAiService
from services.search_service import SearchService
import telebot


# Singletones
openai_service = OpenAiService()
search_service = SearchService()

@bot_instance.message_handler(regexp=r"^(\bgpt\b|\bгпт\b)\s.+")
def msg_handler(message: telebot.types.Message):
    bot_reply = bot_instance.reply_to(message, "generating...")    
    prompt = get_prompt(message.text)
    openai_response = openai_service.get_response(prompt)
    bot_instance.edit_message_text(openai_response, message.chat.id, bot_reply.message_id)

PICTURE_TRIGGERS = ("картинка", "пикча", "image", "img", "picture")

@bot_instance.message_handler(regexp=r"^(\bbot\b|\bбот\b)\s.+")
def img_handler(message: telebot.types.Message):
    prompt = get_prompt(message.text)
    if prompt.startswith(PICTURE_TRIGGERS):
        try:
            picture_prompt = get_prompt(prompt)
            if picture_prompt:
                bot_instance.reply_to(message, "searching...")
                img_link = search_service.get_image(picture_prompt)
                bot_instance.send_photo(message.chat.id, img_link, caption=picture_prompt)
        except Exception as e:
            print(str(e))
            bot_instance.reply_to(message, "Something fucked up")

@bot_instance.message_handler(commands=['clear_context'])
def clr_handler(message: telebot.types.Message):
    openai_service.clear_context()
    bot_instance.reply_to(message, "Context cleared.")

def get_prompt(bot_request):
    return " ".join(bot_request.split(" ")[1:])