# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0007_auto_20160428_0105'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='is_billable',
            field=models.BooleanField(verbose_name='Billable Employee', default=True),
        ),
    ]
