# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0015_reportingperiod_max_working_hours'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportingperiod',
            name='min_working_hours',
            field=models.PositiveSmallIntegerField(default=40),
        ),
    ]
