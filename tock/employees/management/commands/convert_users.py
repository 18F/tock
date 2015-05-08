from django.core.management.base import BaseCommand, CommandError

from django.contrib.auth.models import User

from employees.models import Employee


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for item in User.objects.all():
        	employee, created = Employee.objects.get_or_create(email=item.username)
        	employee.first_name = item.first_name
        	employee.last_name = item.last_name
        	employee.start_date = item.user_data.start_date
        	employee.end_date = item.user_data.end_date
        	employee.is_admin = item.is_staff
        	employee.save()