# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0034_auto_20160810_0314'),
    ]

    operations = [
        migrations.AlterField(
            model_name='engagementinformation',
            name='agmt_end_date',
            field=models.DateField(default=datetime.date(1999, 12, 31), help_text='Enter 7600A, Block 5, "End Date" value.', verbose_name='Agreement period start date'),
        ),
        migrations.AlterField(
            model_name='engagementinformation',
            name='agmt_start_date',
            field=models.DateField(default=datetime.date(1999, 12, 31), help_text='Enter 7600A, Block 5, "Start Date" value.', verbose_name='Agreement period start date'),
        ),
        migrations.AlterField(
            model_name='engagementinformation',
            name='engagement_name',
            field=models.CharField(max_length=200, default='Engagement name is required'),
        ),
        migrations.AlterField(
            model_name='engagementinformation',
            name='engagement_uid',
            field=models.CharField(max_length=200, null=True, help_text='Auto-generated value derived from the first six characters of the engagement name, startdate, and end date. To create, click ', blank=True, verbose_name='Engagement unique ID'),
        ),
        migrations.AlterField(
            model_name='engagementinformation',
            name='iaa_number',
            field=models.CharField(default='IAA number is required', max_length=200, help_text='Enter 7600A, header information,"GT&C #" value.', verbose_name='IAA number'),
        ),
    ]
