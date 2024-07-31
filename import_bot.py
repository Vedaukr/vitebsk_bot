from bot.bot_instance.bot import bot_instance
from utils.import_submodules import import_submodules

# init all handlers
import bot.handlers
import_submodules(bot.handlers)

import scheduler.bot_scheduler
import_submodules(scheduler)
scheduler.bot_scheduler.start_scheduler()