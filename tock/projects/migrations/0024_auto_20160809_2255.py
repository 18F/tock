# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0023_auto_20160809_0400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='end_date',
            field=models.DateField(default=datetime.date(2020, 12, 31), verbose_name='Project End Date', null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='notes_required',
            field=models.BooleanField(default=False, help_text='Check this if notes should be required for time entries against this project.  Note:  Checking this will enable notes to be displayed as well.'),
        ),
        migrations.AlterField(
            model_name='project',
            name='start_date',
            field=models.DateField(blank=True, verbose_name='Project Start Date', null=True),
        ),
        migrations.AlterField(
            model_name='projectalert',
            name='label',
            field=models.CharField(max_length=64, help_text='An optional short label to precede the description, e.g., "Note", "Reminder", etc.', blank=True),
        ),
        migrations.AlterField(
            model_name='projectalert',
            name='title',
            field=models.CharField(max_length=128, help_text='A title to describe the alert so it can be found when linking it to a project.'),
        ),
    ]
