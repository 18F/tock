# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0017_auto_20160708_0156'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reportingperiod',
            old_name='working_hours',
            new_name='exact_working_hours',
        ),
    ]
