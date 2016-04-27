# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import hours.utils
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportingPeriod',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(unique=True)),
                ('end_date', models.DateField()),
                ('working_hours', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(80)], default=40)),
                ('message', models.TextField(blank=True, help_text='A message to provide at the top of the reporting period.')),
            ],
            options={
                'ordering': ['-start_date'],
                'verbose_name': 'Reporting Period',
                'get_latest_by': 'start_date',
                'verbose_name_plural': 'Reporting Periods',
            },
            bases=(hours.utils.ValidateOnSaveMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Timecard',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('submitted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(null=True, auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('reporting_period', models.ForeignKey(to='hours.ReportingPeriod')),
            ],
            options={
                'get_latest_by': 'reporting_period__start_date',
            },
        ),
        migrations.CreateModel(
            name='TimecardObject',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('hours_spent', models.DecimalField(null=True, blank=True, decimal_places=2, max_digits=4)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True, help_text='Please provide details about how you spent your time.', default='')),
                ('project', models.ForeignKey(to='projects.Project')),
                ('timecard', models.ForeignKey(to='hours.Timecard')),
            ],
        ),
        migrations.AddField(
            model_name='timecard',
            name='time_spent',
            field=models.ManyToManyField(to='projects.Project', through='hours.TimecardObject'),
        ),
        migrations.AddField(
            model_name='timecard',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='reportingperiod',
            unique_together=set([('start_date', 'end_date')]),
        ),
        migrations.AlterUniqueTogether(
            name='timecard',
            unique_together=set([('user', 'reporting_period')]),
        ),
    ]
