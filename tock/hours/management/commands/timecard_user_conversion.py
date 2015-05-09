from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from hours.models import Timecard
from employees.models import Employee


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for timecard in Timecard.objects.all():
        	timecard.employee = Employee.objects.get(email=timecard.user.username)
        	timecard.save()