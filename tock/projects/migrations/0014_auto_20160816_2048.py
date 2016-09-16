# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0013_auto_20160816_2014'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='max_hours_restriction',
            field=models.BooleanField(verbose_name='Restrict to max hours', default=False, help_text='Check this to restrict the number of hours logged to the max hours ceiling.'),
        ),
    ]
