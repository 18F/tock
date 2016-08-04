# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0012_auto_20160705_2231'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='auto_deactivate_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='auto_deactivate_days',
            field=models.IntegerField(default=14),
        ),
        migrations.AlterField(
            model_name='project',
            name='end_date',
            field=models.DateField(default=datetime.date(2020, 12, 31), verbose_name='Project End Date'),
        ),
    ]
