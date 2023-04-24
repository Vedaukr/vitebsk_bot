import telebot, random, os
from telebot import types
from utils.dupdetector import DupDetector
from bot_token import bot_token

bot_instance = telebot.TeleBot(token=bot_token, parse_mode=None)

bot_instance.set_my_commands([
    telebot.types.BotCommand("/ping", "Check if alive (debug)"),
    telebot.types.BotCommand("/get_count", "Check images count in db (debug)"),
    telebot.types.BotCommand("/get_rtf", "Получить пожилого ртфченка")
])

SIMILARITY_BITS = 10
dd = DupDetector(SIMILARITY_BITS)
reply_map = {}
media_map = {}

@bot_instance.message_handler(content_types=['photo'])
def handle_img(message: telebot.types.Message):
    fileID = message.photo[-1].file_id
    file_info = bot_instance.get_file(fileID)
    chatId = message.chat.id

    img_info = {
        "ext": file_info.file_path.split('.')[-1],
        "bytes": bot_instance.download_file(file_info.file_path)
    }

    tg_info = {
        "msgId": message.message_id,
        "authorId": message.from_user.id,
        "chatId": chatId,
    }

    sim_arr = dd.detect_duplicate(img_info, tg_info)
    if (len(sim_arr) > 0):
        reply_msg = create_message(sim_arr, chatId)
        reply_markup = get_keyboard(chatId, message.message_id, media_type="i")
        bot_msg = bot_instance.reply_to(message, reply_msg, reply_markup=reply_markup)
        reply_map[str(message.message_id)] = bot_msg.message_id
        media_map[str(message.message_id)] = {
            "media_info": img_info,
            "tg_info": tg_info
        }
    else:
        dd.add_image(img_info, tg_info)

@bot_instance.message_handler(content_types=['video'])
def handle_video(message: telebot.types.Message):
    fileID = message.video.file_id
    file_info = bot_instance.get_file(fileID)
    chatId = message.chat.id
    video = bot_instance.download_file(file_info.file_path)

    tg_info = {
        "msgId": message.message_id,
        "authorId": message.from_user.id,
        "chatId": chatId,
    }

    dup = dd.detect_video_duplicate(video, tg_info)

    if dup:
        reply_msg = create_message([dup], chatId)
        reply_markup = get_keyboard(chatId, message.message_id, media_type="v")
        bot_msg = bot_instance.reply_to(message, reply_msg, reply_markup=reply_markup)
        reply_map[str(message.message_id)] = bot_msg.message_id
        media_map[str(message.message_id)] = {
            "media_info": video,
            "tg_info": tg_info
        }
    else:
        dd.add_video(video, tg_info)

@bot_instance.message_handler(content_types=['sticker'])
def handle_sticker(message: telebot.types.Message):
    if message.sticker.set_name == "arestovych_animated":
        br = bot_instance.reply_to(message, "Arestovich fanboy detected. Destroying...")
        bot_instance.delete_message(message.chat.id, message.message_id)
        bot_instance.delete_message(message.chat.id, br.message_id)

@bot_instance.message_handler(commands=['ping'])
def handle_ping(message: telebot.types.Message):
    bot_instance.reply_to(message, "Alive")

@bot_instance.message_handler(commands=['get_rtf'])
def handle_rtf(message: telebot.types.Message):
    rtf_chanell_id = -1001632815403
    rtf_mes_count = 15358
    while True:
        try:
            msg_id = random.randint(0, rtf_mes_count)
            bot_instance.forward_message(message.chat.id, rtf_chanell_id, msg_id)
            break
        except Exception as e:
            print(e)

@bot_instance.message_handler(commands=['get_count'])
def handle_image_count(message: telebot.types.Message):
    bot_instance.reply_to(message, dd.get_img_count(message.chat.id))

@bot_instance.callback_query_handler(func=lambda call: True)
def command_handler(call):
    qtype, chat_id, msg_id, media_type = call.data.split('|')
    bot_msg_id = reply_map[msg_id]
    bot_instance.delete_message(chat_id, bot_msg_id)
    res = get_from_media_map(msg_id)

    if qtype == 'r':
        bot_instance.delete_message(chat_id, msg_id)

    if qtype == 'f' and res:
        if media_type == 'i':
            dd.add_image(res[0], res[1])
        if media_type == 'v':
            dd.add_video(res[0], res[1])

def get_from_media_map(msg_id):
    if msg_id in media_map:
        res = media_map[msg_id]["media_info"], media_map[msg_id]["tg_info"]
        del media_map[msg_id]
        return res

def create_message(sim_arr, chat_id):
    
    # fix this smh
    chat_id = abs(chat_id) % 10 ** 10
    
    res = "I've found some similar memes:\n"
    for sim in sim_arr:
        dist = sim["dist"]
        msgId = sim["msgId"]
        sim = get_similarity(dist) if dist else "Exact"
        res += f"Link: https://t.me/c/{chat_id}/{msgId}, Similarity: {sim}\n"
    return res

def get_similarity(dist):
    return str(round((64 - dist)/64, 2))

def get_keyboard(chat_id, msg_id, media_type):
    button_1 = types.InlineKeyboardButton('Fuck off, bot', callback_data=f'f|{chat_id}|{msg_id}|{media_type}')
    button_2 = types.InlineKeyboardButton('Delete duplicated meme', callback_data=f'r|{chat_id}|{msg_id}|{media_type}')
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(button_1)
    keyboard.add(button_2)
    return keyboard
