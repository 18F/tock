# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0002_auto_20150120_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agency',
            name='cgac_agency_code',
            field=models.CharField(max_length=3, blank=True, verbose_name='CGAC Agency Code'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='agency',
            name='department',
            field=models.CharField(max_length=200, blank=True, verbose_name='Department'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='agency',
            name='name',
            field=models.CharField(max_length=200, verbose_name='Name'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='agency',
            name='omb_agency_code',
            field=models.CharField(max_length=3, blank=True, verbose_name='OMB Agency Code'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='agency',
            name='omb_bureau_code',
            field=models.CharField(max_length=2, blank=True, verbose_name='OMB Bureau Code'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='agency',
            name='treasury_agency_code',
            field=models.CharField(max_length=2, blank=True, verbose_name='Treasury Agency Code'),
            preserve_default=True,
        ),
    ]
