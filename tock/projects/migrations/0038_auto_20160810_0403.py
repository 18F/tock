# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0037_engagementinformation_engagement_uuid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountingcode',
            name='engagement_uid',
        ),
        migrations.RemoveField(
            model_name='engagementinformation',
            name='engagement_uid',
        ),
        migrations.AddField(
            model_name='accountingcode',
            name='engagement_uuid',
            field=models.CharField(null=True, blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='engagementinformation',
            name='engagement_uuid',
            field=models.UUIDField(default=uuid.uuid4),
        ),
    ]
