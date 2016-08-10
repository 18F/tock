# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0025_auto_20160809_2344'),
    ]

    operations = [
        migrations.CreateModel(
            name='EngagementInformation',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('engagement_name', models.TextField(blank=True, null=True, max_length=200, default='Engagement name is required')),
                ('engagement_uid', models.TextField(blank=True, null=True, max_length=200)),
                ('customer_uid', models.TextField(blank=True, null=True)),
                ('agmt_start_date', models.DateField(verbose_name='Agreement period start date', default=datetime.date(1999, 12, 31))),
                ('agmt_end_date', models.DateField(verbose_name='Agreement period start date', default=datetime.date(1999, 12, 31))),
                ('agency', models.ForeignKey(to='projects.Agency')),
            ],
        ),
        migrations.AlterField(
            model_name='accountingcode',
            name='pp_end_date',
            field=models.DateField(verbose_name='Period ofperformance end date', default=datetime.date(2020, 1, 1)),
        ),
        migrations.AlterField(
            model_name='accountingcode',
            name='pp_start_date',
            field=models.DateField(verbose_name='Period ofperformance start date', default=datetime.date(1999, 12, 31)),
        ),
    ]
