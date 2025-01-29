import gc
import logging
import sys
from scheduler.bot_scheduler import scheduler_instance

MINUTE = 60
logger = logging.getLogger(__name__)

@scheduler_instance.scheduled_job(trigger="interval", seconds=MINUTE*10)
def cleanup_memory_job():
    logger.info("Initiated gc cleanup.")
    gc.collect()
    sys.path_importer_cache.clear()