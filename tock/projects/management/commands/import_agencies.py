import csv
import urllib
import io
from datetime import datetime
import logging
from django.core.management.base import BaseCommand, CommandError

from projects.models import Agency, Project

def process_rows(reader):
    for row in reader:
        department = row[1]
        agency = row[2]
        omb_agency_code = row[3]
        omb_bureau_code = row[4]
        treasury_agency_code = row[5]
        cgac_agency_code = row[6]

        if agency:
            # Simple way to skip row headers
            if agency == "Agency":
                continue
            obj, created = Agency.objects.get_or_create(
                            name=agency,
                            department=department,
                            omb_agency_code=omb_agency_code,
                            omb_bureau_code=omb_bureau_code,
                            treasury_agency_code=treasury_agency_code,
                            cgac_agency_code=cgac_agency_code)
        else:
            continue

def get_list(url):
    response = urllib.request.urlopen(url)
    data = csv.reader(io.TextIOWrapper(response))
    process_rows(data)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if len(args) == 0:
            raise CommandError("No URL to Agency List Provided")

        get_list(args[0])