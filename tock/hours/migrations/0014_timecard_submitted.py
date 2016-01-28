# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def backfill(apps, schema_editor):
    timecard_model = apps.get_model("hours", "Timecard")
    to_submit = timecard_model.objects.filter(time_spent__isnull=False)
    to_submit.update(submitted=True)


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0013_timecardobject_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='timecard',
            name='submitted',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(backfill),
    ]
