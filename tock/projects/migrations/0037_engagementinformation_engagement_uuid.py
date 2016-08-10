# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0036_auto_20160810_0323'),
    ]

    operations = [
        migrations.AddField(
            model_name='engagementinformation',
            name='engagement_uuid',
            field=models.UUIDField(editable=False, default=uuid.uuid4),
        ),
    ]
