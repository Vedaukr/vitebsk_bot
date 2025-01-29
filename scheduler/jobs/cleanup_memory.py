import gc
import logging
import sys
from scheduler.bot_scheduler import scheduler_instance

HOUR = 60*60
logger = logging.getLogger(__name__)

@scheduler_instance.scheduled_job(trigger="interval", seconds=HOUR/4)
def cleanup_memory_job():
    logger.info("Initiated gc cleanup.")
    gc.collect()
    sys.path_importer_cache.clear()