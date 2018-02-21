# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20151103_2041'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='priority',
        ),
    ]
