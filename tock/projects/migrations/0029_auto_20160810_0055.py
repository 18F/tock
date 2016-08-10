# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0028_auto_20160810_0042'),
    ]

    operations = [
        migrations.AddField(
            model_name='engagementinformation',
            name='agmt_estimated_amt',
            field=models.PositiveSmallIntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='accountingcode',
            name='amount',
            field=models.PositiveSmallIntegerField(verbose_name='Order amount($)', default=0),
        ),
    ]
