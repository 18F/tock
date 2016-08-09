# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0015_auto_20160805_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='active',
            field=models.BooleanField(help_text='The active / inactive status of this project is based on the start date, end date, and early warning values for this project and cannot be manually set.', default=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(default='If your reading this, a description for this project is missing and should be added.'),
        ),
    ]
