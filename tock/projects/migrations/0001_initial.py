# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('department', models.CharField(blank=True, max_length=200)),
                ('omb_agency_code', models.CharField(blank=True, max_length=3)),
                ('omb_bureau_code', models.CharField(blank=True, max_length=2)),
                ('treasury_agency_code', models.CharField(blank=True, max_length=2)),
                ('cgac_agency_code', models.CharField(blank=True, max_length=3)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('iaa', models.CharField(blank=True, max_length=200)),
                ('agency', models.ForeignKey(to='projects.Agency')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
