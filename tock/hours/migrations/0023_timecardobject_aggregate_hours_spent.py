# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0022_auto_20160708_0409'),
    ]

    operations = [
        migrations.AddField(
            model_name='timecardobject',
            name='aggregate_hours_spent',
            field=models.DecimalField(blank=True, max_digits=5, decimal_places=2, null=True),
        ),
    ]
