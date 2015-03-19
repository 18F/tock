# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0005_auto_20150318_1433'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timecardobject',
            name='time_percentage',
            field=models.DecimalField(max_digits=3, decimal_places=0, validators=[django.core.validators.MaxValueValidator(100)]),
            preserve_default=True,
        ),
    ]
