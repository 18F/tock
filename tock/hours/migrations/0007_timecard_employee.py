# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0004_employee'),
        ('hours', '0006_auto_20150428_0150'),
    ]

    operations = [
        migrations.AddField(
            model_name='timecard',
            name='employee',
            field=models.ForeignKey(null=True, blank=True, to='employees.Employee'),
            preserve_default=True,
        ),
    ]
