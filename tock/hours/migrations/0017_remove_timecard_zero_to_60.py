# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0016_auto_20160303_0516'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timecard',
            name='zero_to_60',
        ),
    ]
