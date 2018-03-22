from django.apps import AppConfig
from .signals import setup_signals

class EmployeesAppConfig(AppConfig):
    name = "employees"

    def ready(self):
        setup_signals()
