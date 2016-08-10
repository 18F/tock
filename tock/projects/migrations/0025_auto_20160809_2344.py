# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0024_auto_20160809_2255'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accountingcode',
            options={'ordering': ('agency', 'office'), 'verbose_name_plural': 'Order Information', 'verbose_name': 'Order Information'},
        ),
        migrations.AddField(
            model_name='accountingcode',
            name='amount',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Order amount'),
        ),
        migrations.AddField(
            model_name='accountingcode',
            name='pp_end_date',
            field=models.DateField(default=datetime.date(2020, 1, 1), verbose_name='Period ofperformance end date.'),
        ),
        migrations.AddField(
            model_name='accountingcode',
            name='pp_start_date',
            field=models.DateField(default=datetime.date(1999, 12, 31), verbose_name='Period ofperformance start date.'),
        ),
    ]
