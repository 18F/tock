# Generated by Django 2.2.10 on 2020-04-14 19:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0027_auto_20200310_0914'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userdata',
            name='is_billable',
        ),
    ]
