# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0038_auto_20160810_0403'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='engagement',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
