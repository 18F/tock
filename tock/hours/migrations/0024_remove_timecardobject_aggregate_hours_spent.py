# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0023_timecardobject_aggregate_hours_spent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timecardobject',
            name='aggregate_hours_spent',
        ),
    ]
