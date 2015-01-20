# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Week',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('startddate', models.DateField()),
                ('enddate', models.DateField()),
                ('working_hours', models.PositiveSmallIntegerField(validators=[django.core.validators.MaxValueValidator(40)], default=40)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
