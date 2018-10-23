# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

  dependencies = []

  operations = [
      migrations.CreateModel(
          name='AccountingCode',
          fields=[('id', models.AutoField(primary_key=True,
                                          auto_created=True,
                                          verbose_name='ID',
                                          serialize=False)),
                  ('code', models.CharField(blank=True,
                                            max_length=200)),
                  ('office', models.CharField(blank=True,
                                              max_length=200)),
                  ('billable', models.BooleanField(default=False)),],
          options={
              'verbose_name_plural': 'Accounting Codes',
              'verbose_name': 'Accounting Code',
          },
          bases=(models.Model,),),
      migrations.CreateModel(
          name='Agency',
          fields=[('id', models.AutoField(primary_key=True,
                                          auto_created=True,
                                          verbose_name='ID',
                                          serialize=False)),
                  ('name', models.CharField(max_length=200,
                                            verbose_name='Name')),],
          options=
          {'verbose_name_plural': 'Agencies',
           'verbose_name': 'Agency',},
          bases=(models.Model,),),
      migrations.CreateModel(
          name='Project',
          fields=[('id', models.AutoField(primary_key=True,
                                          auto_created=True,
                                          verbose_name='ID',
                                          serialize=False)),
                  ('name', models.CharField(max_length=200)),
                  ('description', models.TextField(blank=True,
                                                   null=True)),
                  ('accounting_code',
                   models.ForeignKey(verbose_name='Accounting Code',
                                     to='projects.AccountingCode', on_delete=models.CASCADE)),],
          options=
          {'verbose_name_plural': 'Projects',
           'verbose_name': 'Project',},
          bases=(models.Model,),),
      migrations.AddField(model_name='accountingcode',
                          name='agency',
                          field=models.ForeignKey(to='projects.Agency', on_delete=models.CASCADE),
                          preserve_default=True,),
  ]
