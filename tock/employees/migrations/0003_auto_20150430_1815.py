# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0002_auto_20150429_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='user',
            field=models.OneToOneField(
                related_name='user_data',
                to=settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE
            ),
            preserve_default=True,
        ),
    ]
