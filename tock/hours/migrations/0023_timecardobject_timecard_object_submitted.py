# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0022_auto_20160708_0409'),
    ]

    operations = [
        migrations.AddField(
            model_name='timecardobject',
            name='timecard_object_submitted',
            field=models.BooleanField(default=False),
        ),
    ]
