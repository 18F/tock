# Generated by Django 3.2.16 on 2022-12-20 18:16

from django.db import migrations
from django.conf import settings


def calculate_total_weekly_allocation(apps, schema_editor):
    Timecard = apps.get_model('hours', 'Timecard')
    timecards = Timecard.objects.all()

    for tc in timecards:
        timecardobjs = tc.timecardobjects.all()
        if len(timecardobjs) == 0:
            continue
        total_allocation_percentage = 0.00
        # have to loop through all timecard objects to get sum of weekly allocation per timecard
        # e.g. Account Managers may bill 12.5% to up to 8 different projects
        # for a total of 100% billable time (or 32 hours)
        for tco in timecardobjs:
            total_allocation_percentage += float(tco.project_allocation)
        tc.total_allocation_percentage = total_allocation_percentage
        tc.total_allocation_hours = total_allocation_percentage * settings.FULLTIME_ALLOCATION_HOURS


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0065_auto_20221219_1407'),
    ]

    operations = [
        migrations.RunPython(calculate_total_weekly_allocation),
    ]
