# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hours', '0020_auto_20160304_0137'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportingperiod',
            name='users',
            field=models.ManyToManyField(blank=True, verbose_name='Zero to 60 users', to=settings.AUTH_USER_MODEL),
        ),
    ]
