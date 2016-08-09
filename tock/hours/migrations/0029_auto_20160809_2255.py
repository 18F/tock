# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0028_auto_20160809_0400'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timecardobject',
            name='timecard_object_submitted',
        ),
        migrations.AddField(
            model_name='timecard',
            name='timecard_object_submitted',
            field=models.BooleanField(default=False),
        ),
    ]
