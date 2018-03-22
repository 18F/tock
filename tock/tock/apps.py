from django.apps import AppConfig

class TockAppConfig(AppConfig):
    name = "tock"

    def ready(self):
        from . import signals  # noqa
