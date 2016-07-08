# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0019_auto_20160708_0210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportingperiod',
            name='exact_working_hours',
            field=models.PositiveSmallIntegerField(default=40),
        ),
        migrations.AlterField(
            model_name='timecardobject',
            name='hours_spent',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=4),
        ),
    ]
