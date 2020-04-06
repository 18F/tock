from django.core.management.base import BaseCommand
from django.db import transaction
from hours.models import Timecard

@transaction.atomic
class Command(BaseCommand):
    help = 'Save every submitted timecard to trigger re-calculation of utilization attributes'


    @transaction.atomic
    def handle(self, *args, **options):
        timecard_total = Timecard.objects.filter(submitted=True).count()
        self.stdout.write(self.style.SUCCESS(f'Updating {timecard_total} timecards...'))

        for timecard in Timecard.objects.filter(submitted=True):
            timecard.save()

        self.stdout.write(self.style.SUCCESS(f'Successfully updated all timecards!'))
