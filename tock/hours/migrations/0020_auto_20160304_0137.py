# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0019_auto_20160304_0135'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reportingperiod',
            old_name='foo_bar',
            new_name='working_hours',
        ),
    ]
