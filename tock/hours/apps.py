from django.apps import AppConfig

class HoursAppConfig(AppConfig):
    name = "hours"

    def ready(self):
        from . import signals  # noqa
