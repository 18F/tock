# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0033_auto_20160810_0246'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountingcode',
            name='notes',
            field=models.TextField(null=True, max_length=200, blank=True),
        ),
        migrations.AddField(
            model_name='engagementinformation',
            name='notes',
            field=models.TextField(null=True, max_length=200, blank=True),
        ),
    ]
