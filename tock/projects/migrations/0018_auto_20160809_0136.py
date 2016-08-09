# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0017_project_aggregate_hours_logged'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='max_hours',
            field=models.IntegerField(help_text='The maximum number of hours that may be logged to this project.', verbose_name='Set maximum hours', default=0),
        ),
    ]
