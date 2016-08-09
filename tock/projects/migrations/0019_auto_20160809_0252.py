# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0018_auto_20160809_0136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='aggregate_hours_logged',
            field=models.IntegerField(default=0, verbose_name='All time hours logged', help_text='All hours logged by users over all reporting periods.'),
        ),
        migrations.AlterField(
            model_name='project',
            name='max_hours',
            field=models.IntegerField(default=0, verbose_name='Set maximum hour ceiling', help_text='When set and "Limit to maximum hours" is checked, this project will deactivate when this ceiling is reached.'),
        ),
    ]
