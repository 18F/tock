# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0022_auto_20160809_0332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='active',
            field=models.BooleanField(help_text='The active / inactive status of this project is based on the start date, end date, early warning values, maximum hour ceiling, and all time hours logged for this project and cannot be manually set.', default=True),
        ),
    ]
