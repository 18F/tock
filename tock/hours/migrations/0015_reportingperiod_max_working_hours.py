# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0014_timecard_submitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportingperiod',
            name='max_working_hours',
            field=models.PositiveSmallIntegerField(default=60),
        ),
    ]
