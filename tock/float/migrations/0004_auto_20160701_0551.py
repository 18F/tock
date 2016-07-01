# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('float', '0003_auto_20160701_0550'),
    ]

    operations = [
        migrations.AlterField(
            model_name='floattasks',
            name='repeat_end',
            field=models.CharField(null=True, max_length=200),
        ),
    ]
