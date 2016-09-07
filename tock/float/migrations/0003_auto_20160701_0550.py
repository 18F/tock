# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('float', '0002_auto_20160630_1836'),
    ]

    operations = [
        migrations.AddField(
            model_name='floattasks',
            name='repeat_end',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='floattasks',
            name='repeat_state',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='floattasks',
            name='start_yr',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='floattasks',
            name='task_days',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='floattasks',
            name='task_notes',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='floattasks',
            name='tentative',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='floattasks',
            name='total_hours',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='floattasks',
            name='client_name',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='floattasks',
            name='created_by',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='floattasks',
            name='hours_pd',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='floattasks',
            name='modified_by',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='floattasks',
            name='person_name',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='floattasks',
            name='project_name',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='floattasks',
            name='task_name',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
