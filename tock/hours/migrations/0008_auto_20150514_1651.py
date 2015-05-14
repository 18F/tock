# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0007_reportingperiod_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportingperiod',
            name='start_date',
            field=models.DateField(unique=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='reportingperiod',
            unique_together=set([('start_date', 'end_date')]),
        ),
    ]
