from bot.bot_instance.bot import bot_instance
from utils.import_submodules import import_submodules

# init all handlers
import bot.handlers
import_submodules(bot.handlers)