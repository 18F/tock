from django.core.management.base import BaseCommand, CommandError

from hours.models import TimecardObject


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        for item in TimecardObject.objects.filter(hours_spent__isnull=True):
        	item.hours_spent = (item.time_percentage/100) * 40
        	item.save()