# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0012_auto_20160705_2231'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='all_hours_logged',
            field=models.DecimalField(blank=True, help_text='All hours logged to this project during all reporting periods by all users.', decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='max_hours',
            field=models.DecimalField(blank=True, decimal_places=2, null=True, verbose_name='Max hours ceiling', help_text='Enter the maximum hours that may be logged to this project.', max_digits=12),
        ),
        migrations.AddField(
            model_name='project',
            name='max_hours_restriction',
            field=models.BooleanField(verbose_name='Restrict to max hours', default=False, help_text='Check this to restrictthe number of hours logged to the max hours ceiling.'),
        ),
    ]
