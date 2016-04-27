# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0005_project_mbnumber'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='notes_displayed',
            field=models.BooleanField(help_text='Check this if a notes field should be displayed along with a time entry against a project.', default=False),
        ),
        migrations.AddField(
            model_name='project',
            name='notes_required',
            field=models.BooleanField(help_text='Check this if notes should be required for time entries against this project.  Note:  Checking this will enable notes to be displayed as well.', default=False),
        ),
    ]
