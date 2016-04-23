# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccountingCode',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, max_length=200)),
                ('office', models.CharField(blank=True, max_length=200)),
                ('billable', models.BooleanField(default=False)),
                ('flat_rate', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Accounting Code',
                'verbose_name_plural': 'Accounting Codes',
            },
        ),
        migrations.CreateModel(
            name='Agency',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Name', help_text="Don't make crappy names!")),
            ],
            options={
                'verbose_name': 'Agency',
                'verbose_name_plural': 'Agencies',
            },
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('mbnumber', models.CharField(blank=True, max_length=200, verbose_name='MB Number')),
                ('description', models.TextField(null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
                ('notes_required', models.BooleanField(help_text='Check this if notes should be required for time entries against this project.  Note:  Checking this will enable notes to be displayed as well.', default=False)),
                ('notes_displayed', models.BooleanField(help_text='Check this if a notes field should be displayed along with a time entry against a project.', default=False)),
                ('accounting_code', models.ForeignKey(to='projects.AccountingCode', verbose_name='Accounting Code')),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
            },
        ),
        migrations.AddField(
            model_name='accountingcode',
            name='agency',
            field=models.ForeignKey(to='projects.Agency'),
        ),
    ]
