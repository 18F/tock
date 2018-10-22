# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0006_userdata_current_employee'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userdata',
            options={'verbose_name_plural': 'Employees', 'verbose_name': 'Employee'},
        ),
        migrations.AddField(
            model_name='userdata',
            name='is_18f_employee',
            field=models.BooleanField(verbose_name='18F Employee', default=True),
        ),
        migrations.AddField(
            model_name='userdata',
            name='unit',
            field=models.IntegerField(verbose_name='Select unit', choices=[(0, 'Operations-Team Operations'), (1, 'Operations-Talent'), (2, 'Operations-Infrastructure'), (3, 'Operations-Front Office'), (4, 'Chapters-Acquisition Managers'), (5, 'Chapters-Engineering'), (6, 'Chapters-Experience Design'), (7, 'Chapters-Product'), (8, 'Chapters-Strategists'), (9, 'Business-Acquisition Services'), (10, 'Business-Custom Partner Solutions'), (11, 'Business-Learn'), (12, 'Business-Products & Platforms'), (13, 'Business-Transformation Services'), (14, 'PIF-Fellows'), (15, 'PIF-Operations'), (16, 'Unknown / N/A')], blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='current_employee',
            field=models.BooleanField(verbose_name='Current Employee', default=True),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='end_date',
            field=models.DateField(verbose_name='Employee end date', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='start_date',
            field=models.DateField(verbose_name='Employee start date', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='userdata',
            name='user',
            field=models.OneToOneField(
                verbose_name='Tock username',
                to=settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
                related_name='user_data'
            ),
        ),
    ]
