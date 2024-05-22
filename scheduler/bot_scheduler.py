import atexit
from apscheduler.schedulers.background import BackgroundScheduler

scheduler_instance = BackgroundScheduler()

def start_scheduler():
    # Add your jobs to the scheduler here.
    scheduler_instance.start()

    # Shut down the scheduler when exiting the app
    atexit.register(scheduler_instance.shutdown)
    