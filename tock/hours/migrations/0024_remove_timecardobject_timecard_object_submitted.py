# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0023_timecardobject_timecard_object_submitted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timecardobject',
            name='timecard_object_submitted',
        ),
    ]
