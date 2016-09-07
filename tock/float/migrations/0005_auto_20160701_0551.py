# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('float', '0004_auto_20160701_0551'),
    ]

    operations = [
        migrations.AlterField(
            model_name='floattasks',
            name='task_notes',
            field=models.CharField(max_length=200, null=True),
        ),
    ]
