# Generated by Django 2.2.12 on 2020-04-23 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0053_auto_20200422_1228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timecardnote',
            name='enabled',
            field=models.BooleanField(default=True, help_text='Toggle whether or not the note is displayed in a timecard. Note that when this is checked any start and end date defined below will be ignored.'),
        ),
    ]
