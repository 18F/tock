# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0009_remove_timecardobject_time_percentage'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reportingperiod',
            options={'ordering': ['-start_date'], 'get_latest_by': 'start_date', 'verbose_name_plural': 'Reporting Periods', 'verbose_name': 'Reporting Period'},
        ),
    ]
