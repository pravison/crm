# business/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from business.functions import add_customers_to_pipeline, follow_up_tasks_today

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(add_customers_to_pipeline, 'cron', hour=1) 
    scheduler.add_job(follow_up_tasks_today, 'cron', hour=9)  # Runs at 4 pm
    scheduler.start()
