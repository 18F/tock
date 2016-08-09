# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0016_auto_20160805_1317'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='aggregate_hours_logged',
            field=models.IntegerField(default=0),
        ),
    ]
