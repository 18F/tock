# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0007_auto_20150319_0134'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Week',
            new_name='ReportingPeriod',
        ),
        migrations.RenameField(
            model_name='timecard',
            old_name='week',
            new_name='reporting_period',
        ),
        migrations.AlterUniqueTogether(
            name='timecard',
            unique_together=set([('user', 'reporting_period')]),
        ),
    ]
