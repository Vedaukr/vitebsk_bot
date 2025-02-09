from settings import settings
import telebot

bot_instance = telebot.TeleBot(token=settings['BOT_TOKEN'], parse_mode=None)

bot_instance.set_my_commands([
    telebot.types.BotCommand("/clear_llm_context", "Clear LLM context"),
    telebot.types.BotCommand("/get_llm_context", "View my LLM context"),
    telebot.types.BotCommand("/get_llm_triggers", "View available llm models"),
    telebot.types.BotCommand("/get_search_triggers", "View available search triggers"),
    telebot.types.BotCommand("/get_dementia_rating", "Dementia rating"),
    telebot.types.BotCommand("/get_rtf", "Получить пожилого ртфченка"),
    telebot.types.BotCommand("/get_random_chat_msg", "Рандомное сообщение из чата"),
    telebot.types.BotCommand("/help", "Bot's capabilities"),
])