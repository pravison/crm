from django.apps import AppConfig


class BusinessConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'business'

    # def ready(self):
    #     from . import scheduler
    #     scheduler.start_scheduler()
