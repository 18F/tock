# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('float', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FloatPeople',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('people_id', models.CharField(blank=True, max_length=200)),
                ('name', models.CharField(blank=True, max_length=500)),
                ('job_title', models.CharField(blank=True, max_length=500)),
                ('email', models.CharField(blank=True, max_length=500)),
                ('description', models.TextField(blank=True)),
                ('im', models.CharField(blank=True, max_length=500)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name_plural': 'Float People Data',
                'verbose_name': 'Float People Data',
            },
        ),
        migrations.AlterField(
            model_name='floattasks',
            name='hours_pd',
            field=models.CharField(blank=True, max_length=200, default=0),
        ),
    ]
