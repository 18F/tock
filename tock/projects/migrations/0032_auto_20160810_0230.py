# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0031_auto_20160810_0150'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accountingcode',
            options={'verbose_name': 'Order Information', 'ordering': ('agency', 'office'), 'verbose_name_plural': 'Order information'},
        ),
        migrations.AlterModelOptions(
            name='agency',
            options={'verbose_name': 'Client', 'verbose_name_plural': 'Clients'},
        ),
        migrations.AlterModelOptions(
            name='projectalert',
            options={'verbose_name': 'Project alert', 'verbose_name_plural': 'Project alerts'},
        ),
        migrations.RenameField(
            model_name='engagementinformation',
            old_name='agency',
            new_name='client',
        ),
        migrations.RemoveField(
            model_name='agency',
            name='name',
        ),
        migrations.RemoveField(
            model_name='engagementinformation',
            name='customer_uid',
        ),
        migrations.AddField(
            model_name='agency',
            name='agency_name',
            field=models.CharField(help_text='Use full agency name, not acronyms.', verbose_name='Client agency name', default='Agency name is required.', max_length=200),
        ),
        migrations.AddField(
            model_name='agency',
            name='office_name',
            field=models.CharField(help_text="Don't use crappy names!", verbose_name='Client office name', default='Office name is required.', max_length=200),
        ),
        migrations.AddField(
            model_name='engagementinformation',
            name='executed',
            field=models.BooleanField(help_text='Whether the inter-agency agreement or other agreement has orhas not been executed by both parties.', verbose_name='Agreement exectued', default=False),
        ),
        migrations.AddField(
            model_name='engagementinformation',
            name='iaa_number',
            field=models.CharField(null=True, verbose_name='IAA Number', help_text='Enter 7600A, header information,"GT&C #" value.', max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='engagementinformation',
            name='agmt_end_date',
            field=models.DateField(help_text='Enter 7600A, Block 5, "End Date"value.', verbose_name='Agreement period start date', default=datetime.date(1999, 12, 31)),
        ),
        migrations.AlterField(
            model_name='engagementinformation',
            name='agmt_estimated_amt',
            field=models.PositiveSmallIntegerField(null=True, verbose_name='Estimated agreement amount', default=0, help_text='Enter 7600A, Block 9, "Total Estimated Amount" value.', blank=True),
        ),
        migrations.AlterField(
            model_name='engagementinformation',
            name='agmt_start_date',
            field=models.DateField(help_text='Enter 7600A, Block 5, "Start Date"value.', verbose_name='Agreement period start date', default=datetime.date(1999, 12, 31)),
        ),
        migrations.AlterField(
            model_name='engagementinformation',
            name='engagement_uid',
            field=models.CharField(null=True, verbose_name='Engagement unique ID', help_text='Auto-generated valuederived from the first six characters of the engagement name, startdate, and end date. To create, click ', max_length=200, blank=True),
        ),
    ]
