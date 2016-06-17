# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0007_auto_20160310_0136'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectAlert',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=128, help_text='A title to describe the alert so it can be found when linking it to a project.')),
                ('label', models.CharField(blank=True, max_length=64, help_text='An optional short label to precede the description, e.g., "Note", "Reminder", etc.')),
                ('description', models.TextField(help_text='The text that is displayed as the note description under a project line item.')),
                ('style', models.CharField(default='', blank=True, max_length=32, help_text='An optional style option to change the display and formatting of the alert.', choices=[('', 'Normal'), ('important', 'Important')])),
            ],
            options={
                'verbose_name': 'Project Alert',
                'verbose_name_plural': 'Project Alerts',
            },
        ),
        migrations.AddField(
            model_name='project',
            name='alerts',
            field=models.ManyToManyField(blank=True, to='projects.ProjectAlert', help_text='Attach one or more alerts to be displayed with this project if need be.'),
        ),
    ]
