# Generated by Django 3.2.6 on 2021-09-30 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hours', '0063_small_allocation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='timecardobject',
            name='project_allocation',
            field=models.DecimalField(choices=[(0, '---'), (1.0, '100%'), (0.5, '50%'), (0.25, '25%'), (0.125, '12.5%')], decimal_places=3, default=0, max_digits=6),
        ),
    ]
