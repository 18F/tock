# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('float', '0006_auto_20160701_0553'),
    ]

    operations = [
        migrations.AddField(
            model_name='floattasks',
            name='im',
            field=models.CharField(null=True, max_length=200),
        ),
        migrations.AddField(
            model_name='floattasks',
            name='tock_pk',
            field=models.ForeignKey(blank=True, null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
