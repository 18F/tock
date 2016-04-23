# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(null=True, blank=True, verbose_name='Employee start date')),
                ('end_date', models.DateField(null=True, blank=True, verbose_name='Employee end date')),
                ('current_employee', models.BooleanField(verbose_name='Is currently employed', default=True)),
                ('is_18f_employee', models.BooleanField(verbose_name='Is 18F employee', default=True)),
                ('unit', models.IntegerField(choices=[(0, 'Operations'), (1, 'Chapters'), (2, 'Business Units'), (3, 'PIF')], null=True, blank=True, verbose_name='Select unit')),
                ('sub_unit', models.IntegerField(choices=[(0, 'Operations-Team Operations'), (1, 'Operations-Talent'), (2, 'Operations-Infrastructure'), (3, 'Operations-Front Office'), (4, 'Chapters-Acquisition Managers'), (5, 'Chapters-Engineering'), (6, 'Chapters-Experience Design'), (7, 'Chapters-Product'), (8, 'Chapters-Strategists'), (9, 'Business-Acquisition Services'), (10, 'Business-Custom Partner Solutions'), (11, 'Business-Learn'), (12, 'Business-Products & Platforms'), (13, 'Business-Transformation Services'), (14, 'PIF-Fellows'), (15, 'PIF-Operations')], null=True, blank=True, verbose_name='Select sub-unit')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, verbose_name='Tock username', related_name='user_data')),
            ],
            options={
                'verbose_name': 'Employee',
                'verbose_name_plural': 'Employees',
            },
        ),
    ]
