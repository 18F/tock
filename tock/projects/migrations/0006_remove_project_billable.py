# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_project_billable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='billable',
        ),
    ]
