# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0003_auto_20150202_0413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timecardobject',
            name='time_percentage',
            field=models.DecimalField(max_digits=3, decimal_places=2, validators=[django.core.validators.MaxValueValidator(1)]),
            preserve_default=True,
        ),
    ]
