# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0027_auto_20160810_0000'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='engagementinformation',
            options={'verbose_name': 'Engagement information', 'verbose_name_plural': 'Engagement information'},
        ),
        migrations.AddField(
            model_name='accountingcode',
            name='engagement',
            field=models.ForeignKey(to='projects.EngagementInformation', default=1),
        ),
        migrations.AlterField(
            model_name='engagementinformation',
            name='engagement_uid',
            field=models.CharField(verbose_name='Engagement unique ID', max_length=200, blank=True, null=True),
        ),
    ]
