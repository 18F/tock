from django.apps import AppConfig
from .signals import setup_signals

class TockAppConfig(AppConfig):
    name = "tock"

    def ready(self):
        setup_signals()
