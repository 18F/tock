# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FloatTasks',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('task_id', models.CharField(blank=True, max_length=200)),
                ('task_name', models.CharField(blank=True, max_length=500)),
                ('people_id', models.CharField(blank=True, max_length=200)),
                ('person_name', models.CharField(blank=True, max_length=500)),
                ('project_id', models.CharField(blank=True, max_length=200)),
                ('project_name', models.CharField(blank=True, max_length=500)),
                ('client_name', models.CharField(blank=True, max_length=500)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
                ('hours_pd', models.DateField(null=True)),
                ('task_cal_days', models.CharField(blank=True, max_length=200)),
                ('created_by', models.CharField(blank=True, max_length=500)),
                ('creator_id', models.CharField(blank=True, max_length=200)),
                ('modified_by', models.CharField(blank=True, max_length=500)),
                ('priority', models.CharField(blank=True, max_length=200)),
            ],
            options={
                'verbose_name': 'Float Task Data',
                'verbose_name_plural': 'Float Task Data',
            },
        ),
    ]
