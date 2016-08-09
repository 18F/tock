# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0014_auto_20160805_1230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='auto_deactivate_date',
            field=models.DateField(default=datetime.date(2020, 12, 17), verbose_name='Early warning deactivation date', help_text='The date on which the project will no longer be available to log hours against. This date is calculated based on the end date of the project and the early warning days value. Default is December 17, 2020.'),
        ),
        migrations.AlterField(
            model_name='project',
            name='auto_deactivate_days',
            field=models.IntegerField(default=14, verbose_name='Set early warning days', help_text='Set the number of calendar days prior to the end date when this project will no longer be available to log hours against. Default is 14 days.'),
        ),
        migrations.AlterField(
            model_name='project',
            name='description',
            field=models.TextField(default='If your reading this, a descriptionfor this project is missing and should be added.'),
        ),
        migrations.AlterField(
            model_name='project',
            name='end_date',
            field=models.DateField(default=datetime.date(2020, 12, 31), verbose_name='Set project end date', null=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='max_hours',
            field=models.IntegerField(verbose_name='Set maximum hours', help_text='The maximum number of hours that may be logged to this project.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='max_hours_restriction',
            field=models.BooleanField(default=False, verbose_name='Limit to maximum hours', help_text='Check this to enforce the maximum hours ceiling.'),
        ),
        migrations.AlterField(
            model_name='project',
            name='start_date',
            field=models.DateField(verbose_name='Set project start date', null=True, blank=True),
        ),
    ]
