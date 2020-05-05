# Generated by Django 2.2.12 on 2020-05-05 13:25

from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0029_remove_userdata_is_18f_employee'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userdata',
            name='billable_expectation',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.8000000000000000444089209850062616169452667236328125'), help_text='Percentage of hours (expressed as a decimal) expected to be billable each week', max_digits=3, validators=[django.core.validators.MaxValueValidator(limit_value=1)]),
        ),
    ]
