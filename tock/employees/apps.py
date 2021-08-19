from django.apps import AppConfig
from .signals import setup_signals

class EmployeesAppConfig(AppConfig):
    name = "employees"
    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        setup_signals()
