# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0003_auto_20150430_1815'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('email', models.EmailField(verbose_name='Email Address', max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=255, blank=True)),
                ('last_name', models.CharField(max_length=255, blank=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('is_admin', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
