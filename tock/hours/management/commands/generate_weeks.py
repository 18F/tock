import csv
import urllib
import io
from datetime import datetime
import logging

from django.core.management.base import BaseCommand, CommandError

from hours.models import Week

'''
TODO
def get_next_weekday(day):
    weekday = datetime.weekday(day)
    if weekday < 5:
        return day
    print(weekday)

def get_weeks(FY):
    # First determine the starting day
    first_weekday = get_next_weekday(datetime.strptime('%s-10-01' % FY, '%Y-%m-%d'))



class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if len(args) == 0:
            raise CommandError("No Fiscal Year Provided!")

        get_weeks(int(args[0]))
'''