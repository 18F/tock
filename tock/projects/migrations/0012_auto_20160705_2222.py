# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_auto_20160608_2143'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='accountingcode',
            options={'verbose_name': 'Accounting Code', 'ordering': ('agency', 'office'), 'verbose_name_plural': 'Accounting Codes'},
        ),
    ]
