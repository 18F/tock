# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountingcode',
            name='flat_rate',
<<<<<<< HEAD
            field=models.BooleanField(default=False)
            ),

        migrations.AddField(
            model_name='project',
            name='mb_number',
            field=models.CharField(max_length=200, blank=True)
            ),

        migrations.AddField(
            model_name='project',
            name='active',
            field=models.BooleanField(blank=True)
            ),

        migrations.AddField(
            model_name='accountingcode',
            name='investment',
            field=models.BooleanField(blank=True)
            ),

=======
            field=models.BooleanField(default=False),
        ),
>>>>>>> parent of 2b6c084... test-branch-commits
        migrations.AlterField(
            model_name='agency',
            name='name',
            field=models.CharField(help_text="Don't make crappy names!", verbose_name='Name', max_length=200),
        ),
    ]
