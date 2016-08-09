# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0027_remove_reportingperiod_active_projects'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timecardobject',
            old_name='submitted',
            new_name='timecard_object_submitted',
        ),
    ]
