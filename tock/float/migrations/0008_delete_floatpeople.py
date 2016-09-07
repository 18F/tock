# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('float', '0007_auto_20160824_0307'),
    ]

    operations = [
        migrations.DeleteModel(
            name='FloatPeople',
        ),
    ]
