import telebot

def create_message(sim_arr, chat_id):
    
    # fix this smh
    chat_id = normalize_tg_chat_id(chat_id)
    
    res = "I've found some similar memes:\n"
    for sim in sim_arr:
        dist = sim["dist"]
        msgId = sim["msgId"]
        sim = get_similarity(dist) if dist else "Exact"
        res += f"Link: https://t.me/c/{chat_id}/{msgId}, Similarity: {sim}\n"
    return res

def get_similarity(dist):
    return str(round((64 - dist)/64, 2))

def get_keyboard(chat_id, msg_id):
    button_1 = telebot.types.InlineKeyboardButton('Fuck off, bot', callback_data=f'f|{chat_id}|{msg_id}')
    button_2 = telebot.types.InlineKeyboardButton('Delete duplicated meme', callback_data=f'r|{chat_id}|{msg_id}')
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(button_1)
    keyboard.add(button_2)
    return keyboard

def normalize_tg_chat_id(chat_id):
    return abs(chat_id) % 10 ** 10