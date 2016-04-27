# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0004_remove_project_priority'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='mbnumber',
            field=models.CharField(blank=True, max_length=200, verbose_name='MB Number'),
        ),
    ]
