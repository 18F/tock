# Generated by Django 2.2.12 on 2020-05-05 01:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0028_remove_userdata_is_billable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdata',
            name='is_18f_employee',
        ),
    ]
