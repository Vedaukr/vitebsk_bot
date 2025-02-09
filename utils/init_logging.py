import logging
import logging.config
import os
from logging.handlers import TimedRotatingFileHandler

from settings import settings
LOGS_PATH = settings.get('LOGS_PATH', './logs/app.log')

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    
    # Add console handler to the logger
    logger.addHandler(ch)

    if not os.path.exists(os.path.dirname(LOGS_PATH)):
        os.makedirs(os.path.dirname(LOGS_PATH))

    # Create a timed rotating file handler for rotating logs by day
    date_based_handler = TimedRotatingFileHandler(LOGS_PATH, when='midnight', interval=1, backupCount=30) 
    date_based_handler.suffix = "%Y-%m-%d"
    date_based_handler.setFormatter(formatter)
    date_based_handler.namer = lambda name: name.replace(".log", "") + ".log"

    # Add date-based file handler to the logger
    logger.addHandler(date_based_handler)


