# Generated by Django 5.1.1 on 2024-09-22 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0040_alter_region_units_here_dict_alter_round_has_started'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='protection_ticks_remaining',
            field=models.IntegerField(default=96),
        ),
    ]
