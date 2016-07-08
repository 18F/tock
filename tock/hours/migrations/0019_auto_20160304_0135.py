# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0018_timecard_zero_to_60'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reportingperiod',
            old_name='working_hours',
            new_name='foo_bar',
        ),
    ]
