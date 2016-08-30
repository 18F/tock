# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import employees.models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0010_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserTravelRequest',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('requestor_name', models.CharField(max_length=255, verbose_name='Requestor Name')),
                ('requestor_email', models.EmailField(max_length=255, verbose_name='Requestor Email')),
                ('billability', models.CharField(max_length=255, verbose_name='Billability', choices=[('billable', 'billable'), ('non-billable', 'non-billable')])),
                ('tock_project_name', models.CharField(max_length=255, verbose_name='Project Name', help_text='Exact name of the Tock project')),
                ('tock_project_id', models.CharField(max_length=255, verbose_name='Project ID', help_text='Please look up Tock project here: <a href="https://tock.18f.gov/projects/">https://tock.18f.gov/projects/</a>.')),
                ('client_email', models.EmailField(max_length=255, verbose_name='Client Email', help_text='Or supervisor, if non-billable.')),
                ('home_location', models.CharField(max_length=255, verbose_name='Home Location', help_text='Where you are usually located.')),
                ('work_location', models.CharField(max_length=255, verbose_name='Work Location', help_text='Where you will be traveling to.')),
                ('work_to_be_done', models.TextField(max_length=1023, verbose_name='Work to be Done', help_text='What you will be working on.')),
                ('departure_date', models.DateField(validators=[employees.models.validate_today_or_later], verbose_name='Departure Date')),
                ('return_date', models.DateField(validators=[employees.models.validate_today_or_later], verbose_name='Return Date')),
                ('first_day_of_travel_work_date', models.DateField(validators=[employees.models.validate_today_or_later], verbose_name='First Day of Travel Work Date')),
            ],
        ),
    ]
