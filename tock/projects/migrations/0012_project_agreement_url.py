# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0011_auto_20160608_2143'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='agreement_URL',
            field=models.URLField(verbose_name='Link to Agreement Folder', blank=True, max_length=1000),
        ),
    ]
