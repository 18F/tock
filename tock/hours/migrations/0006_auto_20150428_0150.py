# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0005_auto_20150413_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='timecardobject',
            name='hours_spent',
            field=models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='timecardobject',
            name='time_percentage',
            field=models.DecimalField(max_digits=4, decimal_places=1, blank=True, validators=[django.core.validators.MaxValueValidator(100)], null=True),
            preserve_default=True,
        ),
    ]
