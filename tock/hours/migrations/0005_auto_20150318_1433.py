# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0004_auto_20150202_1735'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timecard',
            name='user',
            field=models.CharField(max_length=255),
            preserve_default=True,
        ),
    ]
