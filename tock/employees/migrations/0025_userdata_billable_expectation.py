# Generated by Django 2.2.7 on 2019-12-19 14:25

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0024_auto_20171229_1156'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdata',
            name='billable_expectation',
            field=models.DecimalField(decimal_places=2, default=0.8, max_digits=3, validators=[django.core.validators.MaxValueValidator(limit_value=1)], verbose_name='Percentage of hours which are expected to be billable each week'),
        ),
    ]