# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-10-12 20:46
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0015_auto_20161006_1016'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userdata',
            options={'ordering': ['user__last_name'], 'verbose_name': 'Employee', 'verbose_name_plural': 'Employees'},
        ),
    ]
