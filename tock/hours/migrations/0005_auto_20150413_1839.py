# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0004_auto_20150408_1934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timecardobject',
            name='time_percentage',
            field=models.DecimalField(max_digits=4, validators=[django.core.validators.MaxValueValidator(100)], decimal_places=1),
            preserve_default=True,
        ),
    ]
