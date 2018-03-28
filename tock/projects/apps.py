from django.apps import AppConfig
from .signals import setup_signals

class ProjectsAppConfig(AppConfig):
    name = "projects"

    def ready(self):
        setup_signals()
