# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0026_auto_20160809_2357'),
    ]

    operations = [
        migrations.AlterField(
            model_name='engagementinformation',
            name='engagement_name',
            field=models.CharField(blank=True, max_length=200, default='Engagement name is required', null=True),
        ),
        migrations.AlterField(
            model_name='engagementinformation',
            name='engagement_uid',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
