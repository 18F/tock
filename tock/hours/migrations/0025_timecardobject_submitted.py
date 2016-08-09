# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0024_remove_timecardobject_aggregate_hours_spent'),
    ]

    operations = [
        migrations.AddField(
            model_name='timecardobject',
            name='submitted',
            field=models.BooleanField(default=False),
        ),
    ]
