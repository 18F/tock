# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0013_auto_20160804_0228'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='max_hours',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='max_hours_restriction',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='project',
            name='notes_required',
            field=models.BooleanField(help_text='Check this if notes should be required for time entriesagainst this project.  Note: Checking this will enable notes tobe displayed as well.', default=False),
        ),
        migrations.AlterField(
            model_name='projectalert',
            name='label',
            field=models.CharField(help_text='An optional short label to precede the description, e.g.,"Note", "Reminder", etc.', max_length=64, blank=True),
        ),
        migrations.AlterField(
            model_name='projectalert',
            name='title',
            field=models.CharField(help_text='A title to describe the alert so it can be found whenlinking it to a project.', max_length=128),
        ),
    ]
