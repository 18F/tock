# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0014_timecard_submitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='timecard',
            name='more_than_60',
            field=models.BooleanField(default=False),
        ),
    ]
