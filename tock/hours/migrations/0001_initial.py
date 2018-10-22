# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import hours.utils
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

  dependencies = [('projects', '0001_initial'),
                  migrations.swappable_dependency(settings.AUTH_USER_MODEL),]

  operations = [
      migrations.CreateModel(
          name='ReportingPeriod',
          fields=[('id', models.AutoField(primary_key=True,
                                          auto_created=True,
                                          verbose_name='ID',
                                          serialize=False)),
                  ('start_date', models.DateField()),
                  ('end_date', models.DateField()),
                  ('working_hours', models.PositiveSmallIntegerField(
                      default=40,
                      validators=[django.core.validators.MaxValueValidator(
                          40)])),],
          options={
              'verbose_name_plural': 'Reporting Periods',
              'verbose_name': 'Reporting Period',
          },
          bases=(hours.utils.ValidateOnSaveMixin, models.Model),),
      migrations.CreateModel(name='Timecard',
                             fields=[('id', models.AutoField(primary_key=True,
                                                             auto_created=True,
                                                             verbose_name='ID',
                                                             serialize=False)),
                                     ('reporting_period', models.ForeignKey(
                                         to='hours.ReportingPeriod',
                                         on_delete=models.CASCADE)),],
                             options={},
                             bases=(models.Model,),),
      migrations.CreateModel(
          name='TimecardObject',
          fields=[('id', models.AutoField(primary_key=True,
                                          auto_created=True,
                                          verbose_name='ID',
                                          serialize=False)),
                  ('time_percentage', models.DecimalField(
                      decimal_places=0,
                      validators=[django.core.validators.MaxValueValidator(100)],
                      max_digits=3)),
                  ('created', models.DateTimeField(auto_now_add=True)),
                  ('modified', models.DateTimeField(auto_now=True)),
                  ('project', models.ForeignKey(to='projects.Project', on_delete=models.CASCADE)),
                  ('timecard', models.ForeignKey(to='hours.Timecard', on_delete=models.CASCADE)),],
          options={},
          bases=(models.Model,),),
      migrations.AddField(
          model_name='timecard',
          name='time_spent',
          field=models.ManyToManyField(through='hours.TimecardObject',
                                       to='projects.Project'),
          preserve_default=True,),
      migrations.AddField(model_name='timecard',
                          name='user',
                          field=models.ForeignKey(
                              to=settings.AUTH_USER_MODEL,
                              on_delete=models.CASCADE),
                              preserve_default=True,
                          ),
      migrations.AlterUniqueTogether(
          name='timecard',
          unique_together=set([('user', 'reporting_period')]),),
  ]
