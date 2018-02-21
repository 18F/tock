# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0008_auto_20150514_1651'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timecardobject',
            name='time_percentage',
        ),
    ]
