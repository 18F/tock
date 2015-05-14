# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0006_auto_20150428_0150'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportingperiod',
            name='message',
            field=models.TextField(blank=True, help_text='A message to provide at the top of the reporting period.'),
            preserve_default=True,
        ),
    ]
