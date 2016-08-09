# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0019_auto_20160809_0252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='max_hours',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='Maximum hour ceiling', help_text='When set and "Limit to maximum hours" is checked, this project will deactivate when this ceiling is reached.'),
        ),
    ]
