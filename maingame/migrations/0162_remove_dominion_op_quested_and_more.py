# Generated by Django 5.1.1 on 2025-02-13 04:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0161_discovery_repeatable'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dominion',
            name='op_quested',
        ),
        migrations.AlterField(
            model_name='dominion',
            name='complacency',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='dominion',
            name='determination',
            field=models.FloatField(default=0),
        ),
    ]
