from django.apps import AppConfig
from .signals import setup_signals

class OrganizationsAppConfig(AppConfig):
    name = "organizations"

    def ready(self):
        setup_signals()
