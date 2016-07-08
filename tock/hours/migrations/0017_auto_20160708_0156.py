# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0016_reportingperiod_min_working_hours'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reportingperiod',
            options={'ordering': ['-end_date'], 'verbose_name': 'Reporting Period', 'get_latest_by': 'end_date', 'verbose_name_plural': 'Reporting Periods'},
        ),
        migrations.AlterModelOptions(
            name='timecard',
            options={'get_latest_by': 'reporting_period__end_date'},
        ),
        migrations.AlterField(
            model_name='reportingperiod',
            name='end_date',
            field=models.DateField(unique=True),
        ),
    ]
