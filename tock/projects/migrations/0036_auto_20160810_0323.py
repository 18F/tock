# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0035_auto_20160810_0318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountingcode',
            name='agency',
            field=models.ForeignKey(to='projects.Agency', default=1),
        ),
        migrations.AlterField(
            model_name='engagementinformation',
            name='engagement_uid',
            field=models.CharField(help_text='Auto-generated value derived from the first six characters of the engagement name, startdate, and end date, plus a database key. To create, click ', max_length=200, blank=True, verbose_name='Engagement unique ID', null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='accounting_code',
            field=models.ForeignKey(to='projects.AccountingCode', verbose_name='Related order information'),
        ),
    ]
