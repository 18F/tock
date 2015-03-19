# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0008_auto_20150319_1440'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reportingperiod',
            options={'verbose_name_plural': 'Reporting Periods', 'verbose_name': 'Reporting Period'},
        ),
    ]
