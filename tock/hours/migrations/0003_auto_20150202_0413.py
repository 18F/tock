# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hours', '0002_auto_20150121_0913'),
    ]

    operations = [
        migrations.AddField(
            model_name='timecard',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, default=1),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='timecard',
            unique_together=set([('user', 'week')]),
        ),
        migrations.RemoveField(
            model_name='timecard',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='timecard',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='timecard',
            name='email',
        ),
    ]
