# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0010_auto_20150519_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportingperiod',
            name='working_hours',
            field=models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(60)], default=40),
        ),
    ]
