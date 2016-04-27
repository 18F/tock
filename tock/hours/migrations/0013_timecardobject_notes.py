# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0012_auto_20151224_1625'),
    ]

    operations = [
        migrations.AddField(
            model_name='timecardobject',
            name='notes',
            field=models.TextField(help_text='Please provide details about how you spent your time.', blank=True, default=''),
        ),
    ]
