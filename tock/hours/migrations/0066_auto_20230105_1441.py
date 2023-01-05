# Generated by Django 3.2.16 on 2023-01-05 19:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0065_auto_20221219_1407'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timecard',
            name='total_allocation_hours',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, editable=False, max_digits=5, null=True, verbose_name='# of hours which are calculated from weekly allocation %'),
        ),
        migrations.AlterField(
            model_name='timecard',
            name='total_weekly_allocation',
            field=models.DecimalField(blank=True, decimal_places=5, default=0, editable=False, max_digits=6, null=True, verbose_name='total weekly allocation %, sum of project_allocation from related timecardobjects'),
        ),
    ]
