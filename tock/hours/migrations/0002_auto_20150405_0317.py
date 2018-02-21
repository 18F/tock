# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

  dependencies = [('hours', '0001_initial'),]

  operations = [
      migrations.AlterModelOptions(
          name='reportingperiod',
          options={
              'verbose_name': 'Reporting Period',
              'verbose_name_plural': 'Reporting Periods',
              'get_latest_by': 'start_date'
          },),
      migrations.AlterModelOptions(
          name='timecard',
          options={'get_latest_by': 'reporting_period__start_date'},),
  ]
