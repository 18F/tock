# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0029_auto_20160810_0055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountingcode',
            name='engagement',
            field=models.ForeignKey(to='projects.EngagementInformation'),
        ),
    ]
