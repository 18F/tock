# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0039_project_engagement'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='engagementinformation',
            name='engagement_name',
        ),
        migrations.AlterField(
            model_name='accountingcode',
            name='egmt_agency',
            field=models.CharField(null=True, max_length=200, blank=True, verbose_name='Client agency'),
        ),
        migrations.AlterField(
            model_name='accountingcode',
            name='egmt_office',
            field=models.CharField(null=True, max_length=200, blank=True, verbose_name='Client office'),
        ),
        migrations.AlterField(
            model_name='accountingcode',
            name='engagement_uuid',
            field=models.CharField(null=True, max_length=200, blank=True, verbose_name='Engagement unique ID'),
        ),
    ]
