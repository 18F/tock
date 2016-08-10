# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0032_auto_20160810_0230'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountingcode',
            name='egmt_agency',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='accountingcode',
            name='egmt_office',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='accountingcode',
            name='engagement_uid',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
    ]
