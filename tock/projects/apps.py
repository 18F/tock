from django.apps import AppConfig
from .signals import setup_signals

class ProjectsAppConfig(AppConfig):
    name = "projects"
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        setup_signals()
