# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0018_auto_20160809_0136'),
        ('hours', '0025_timecardobject_submitted'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportingperiod',
            name='active_projects',
            field=models.ManyToManyField(to='projects.Project'),
        ),
    ]
