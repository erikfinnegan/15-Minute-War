# Generated by Django 5.1.1 on 2024-09-20 03:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0027_alter_player_building_types_available'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='building_types_available',
            field=models.ManyToManyField(blank=True, to='maingame.buildingtype'),
        ),
    ]
