# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0003_auto_20150120_1836'),
        ('hours', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Timecard',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TimecardObject',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('time_percentage', models.DecimalField(decimal_places=2, max_digits=3)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('project', models.ForeignKey(to='projects.Project')),
                ('timecard', models.ForeignKey(to='hours.Timecard')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='timecard',
            name='time_spent',
            field=models.ManyToManyField(through='hours.TimecardObject', to='projects.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='timecard',
            name='week',
            field=models.ForeignKey(to='hours.Week'),
            preserve_default=True,
        ),
        migrations.RenameField(
            model_name='week',
            old_name='enddate',
            new_name='end_date',
        ),
        migrations.RenameField(
            model_name='week',
            old_name='startddate',
            new_name='start_date',
        ),
    ]
