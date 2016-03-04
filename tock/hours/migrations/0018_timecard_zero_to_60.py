# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0017_remove_timecard_zero_to_60'),
    ]

    operations = [
        migrations.AddField(
            model_name='timecard',
            name='zero_to_60',
            field=models.BooleanField(default=False),
        ),
    ]
