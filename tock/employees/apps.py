from django.apps import AppConfig

class EmployeesAppConfig(AppConfig):
    name = "employees"

    def ready(self):
        from . import signals  # noqa
