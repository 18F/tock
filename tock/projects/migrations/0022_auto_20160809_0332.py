# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0021_auto_20160809_0330'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='aggregate_hours_logged',
            field=models.DecimalField(null=True, default=0.0, max_digits=10, help_text='All hours logged by users over all reporting periods.', decimal_places=2, verbose_name='All time hours logged', blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='max_hours',
            field=models.DecimalField(null=True, default=0.0, max_digits=10, help_text='When set and "Limit to maximum hours" is checked, this project will deactivate when this ceiling is reached.', decimal_places=2, verbose_name='Maximum hour ceiling', blank=True),
        ),
    ]
