# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0010_auto_20160609_0239'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='end_date',
            field=models.DateField(null=True, verbose_name='Project End Date', blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='start_date',
            field=models.DateField(null=True, verbose_name='Project Start Date', blank=True),
        ),
    ]
