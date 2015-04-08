# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0003_auto_20150408_1934'),
    ]

    operations = [
        migrations.RenameField(
            model_name='timecard',
            old_name='created_at',
            new_name='created',
        ),
        migrations.RenameField(
            model_name='timecard',
            old_name='updated_at',
            new_name='modified',
        ),
    ]
