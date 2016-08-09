# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0020_auto_20160809_0254'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='max_hours',
            field=models.DecimalField(null=True, help_text='When set and "Limit to maximum hours" is checked, this project will deactivate when this ceiling is reached.', blank=True, max_digits=5, decimal_places=2, default=0.0, verbose_name='Maximum hour ceiling'),
        ),
    ]
