# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0008_userdata_is_billable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='current_employee',
            field=models.BooleanField(verbose_name='Is Current Employee', default=True),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='is_18f_employee',
            field=models.BooleanField(verbose_name='Is 18F Employee', default=True),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='is_billable',
            field=models.BooleanField(verbose_name='Is 18F Billable Employee', default=True),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='unit',
            field=models.IntegerField(verbose_name='Select 18F unit', choices=[(0, 'Operations-Team Operations'), (1, 'Operations-Talent'), (2, 'Operations-Infrastructure'), (3, 'Operations-Front Office'), (4, 'Chapters-Acquisition Managers'), (5, 'Chapters-Engineering'), (6, 'Chapters-Experience Design'), (7, 'Chapters-Product'), (8, 'Chapters-Strategists'), (9, 'Business-Acquisition Services'), (10, 'Business-Custom Partner Solutions'), (11, 'Business-Learn'), (12, 'Business-Products & Platforms'), (13, 'Business-Transformation Services'), (14, 'PIF-Fellows'), (15, 'PIF-Operations'), (16, 'Unknown / N/A')], blank=True, null=True),
        ),
    ]
