# Generated by Django 2.2.12 on 2020-05-07 20:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0031_userdata_expected_billable_hours'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdata',
            name='billable_expectation',
        ),
    ]
