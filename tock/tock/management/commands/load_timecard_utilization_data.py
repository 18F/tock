import csv
from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from hours.models import Timecard, ReportingPeriod


@transaction.atomic
class Command(BaseCommand):
    help = 'Load CSV file of (username, target_hours, from_date) to bulk update timecard billing expectation values'

    def add_arguments(self, parser):
        parser.add_argument('csv_path', nargs='+', type=str)

    def _update_timecard(self, timecard, target_hours):
        """Update billable expectation from provided target hours and save"""
        if target_hours == 0:
            timecard.billable_expectation = 0
        else:
            timecard.billable_expectation = Decimal(target_hours / 40.0)
        timecard.save()

    @transaction.atomic
    def handle(self, *args, **options):
        for source_file in options['csv_path']:
            self.stdout.write(f'Loading timecard data from {source_file}')
            try:
                with open(source_file, newline='') as csvfile:
                    reader = csv.reader(csvfile)
                    for username, target, from_date in reader:
                        # Tock reporting period spans fiscal years at start of FY20
                        # If from_date in input is 10/1/19, get all FY20 timecards
                        if from_date == '10/1/2019':
                            start_date = ReportingPeriod.get_fiscal_year_start_date(2020)
                        else:
                            start_date = datetime.strptime(from_date, '%m/%d/%Y')

                        timecards = Timecard.objects.filter(user__username=username, reporting_period__start_date__gte=start_date)
                        self.stdout.write(f'Updating {len(timecards)} timecards for {username} to target hours {target}')

                        # Update all identified timecards
                        [self._update_timecard(timecard, float(target)) for timecard in timecards]
            except FileNotFoundError:
                self.stdout.write(self.style.ERROR(f'File not found : {source_file}'))

