# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0026_reportingperiod_active_projects'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reportingperiod',
            name='active_projects',
        ),
    ]
