from django.apps import AppConfig
import os


class OsiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Osi'
    verbose_name = 'Расчет КОС'

    def ready(self):
        from .scheduler import scheduler
        if os.environ.get('RUN_MAIN', None) != 'true':
            scheduler.start()