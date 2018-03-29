from django.apps import AppConfig
from .signals import setup_signals

class HoursAppConfig(AppConfig):
    name = "hours"

    def ready(self):
        setup_signals()
