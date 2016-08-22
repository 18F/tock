# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0021_auto_20160708_0406'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timecardobject',
            name='hours_spent',
            field=models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True),
        ),
    ]
