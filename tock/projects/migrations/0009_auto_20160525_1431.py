# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0008_auto_20160525_0535'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectalert',
            name='style_bold',
            field=models.BooleanField(help_text='A toggle for whether or not the alert should also be bold.', default=False),
        ),
        migrations.AddField(
            model_name='projectalert',
            name='style_italic',
            field=models.BooleanField(help_text='A toggle for whether or not the alert should also be italicized.', default=False),
        ),
        migrations.AlterField(
            model_name='projectalert',
            name='style',
            field=models.CharField(choices=[('', 'Normal'), ('info', 'Info'), ('important', 'Important'), ('warning', 'Warning')], max_length=32, blank=True, help_text='An optional style option to change the display and formatting of the alert.', default=''),
        ),
    ]
