# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0020_auto_20160708_0404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timecardobject',
            name='hours_spent',
            field=models.DecimalField(blank=True, decimal_places=2, null=True, max_digits=4),
        ),
    ]
