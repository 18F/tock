# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0004_employee'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Employee',
        ),
    ]
