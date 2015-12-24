# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0011_auto_20151203_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportingperiod',
            name='working_hours',
            field=models.PositiveSmallIntegerField(default=40, validators=[django.core.validators.MaxValueValidator(80)]),
        ),
    ]
