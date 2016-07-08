# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0015_timecard_more_than_60'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timecard',
            old_name='more_than_60',
            new_name='zero_to_60',
        ),
    ]
