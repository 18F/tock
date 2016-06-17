# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0009_auto_20160525_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectalert',
            name='destination_url',
            field=models.URLField(max_length=512, help_text='An optional URL to wrap the alert in, e.g. pointing to some additional documentation around a time tracking policy.', blank=True),
        ),
        migrations.AlterField(
            model_name='projectalert',
            name='style',
            field=models.CharField(max_length=32, help_text='An optional style option to change the display and formatting of the alert.', default='', choices=[('', 'No style'), ('info', 'Info'), ('important', 'Important'), ('warning', 'Warning')], blank=True),
        ),
        migrations.AlterField(
            model_name='projectalert',
            name='style_bold',
            field=models.BooleanField(help_text='A toggle for whether or not the alert should also be bold. Not applicable when no style is selected.', default=False),
        ),
        migrations.AlterField(
            model_name='projectalert',
            name='style_italic',
            field=models.BooleanField(help_text='A toggle for whether or not the alert should also be italicized. Not applicable when no style is selected.', default=False),
        ),
    ]
