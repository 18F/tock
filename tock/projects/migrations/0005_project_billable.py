# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_project_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='billable',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
