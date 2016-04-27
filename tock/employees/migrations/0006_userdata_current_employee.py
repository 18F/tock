# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0005_delete_employee'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='current_employee',
            field=models.BooleanField(default=True),
        ),
    ]
