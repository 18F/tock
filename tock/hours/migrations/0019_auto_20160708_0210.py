# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0018_auto_20160708_0207'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reportingperiod',
            options={'verbose_name': 'Reporting Period', 'get_latest_by': 'start_date', 'verbose_name_plural': 'Reporting Periods', 'ordering': ['-start_date']},
        ),
        migrations.AlterModelOptions(
            name='timecard',
            options={'get_latest_by': 'reporting_period__start_date'},
        ),
    ]
