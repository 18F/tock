# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='agency',
            options={'verbose_name_plural': 'Agencies', 'verbose_name': 'Agency'},
        ),
        migrations.AlterModelOptions(
            name='project',
            options={'verbose_name_plural': 'Projects', 'verbose_name': 'Project'},
        ),
    ]
