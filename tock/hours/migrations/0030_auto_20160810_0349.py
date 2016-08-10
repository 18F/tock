# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0029_auto_20160809_2255'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reportingperiod',
            options={'get_latest_by': 'start_date', 'verbose_name': 'Reporting period', 'verbose_name_plural': 'Reporting periods', 'ordering': ['-start_date']},
        ),
    ]
