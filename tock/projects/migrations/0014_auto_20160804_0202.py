# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0013_auto_20160804_0130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='auto_deactivate_date',
            field=models.DateField(default=datetime.date(2020, 12, 17)),
        ),
    ]
