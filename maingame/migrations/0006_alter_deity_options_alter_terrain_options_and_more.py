# Generated by Django 5.1.1 on 2024-09-17 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0005_remove_building_housing_buildingtype_housing'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deity',
            options={'verbose_name_plural': 'deities'},
        ),
        migrations.AlterModelOptions(
            name='terrain',
            options={'verbose_name_plural': 'Terrain'},
        ),
        migrations.RenameField(
            model_name='player',
            old_name='starter_units',
            new_name='units_available',
        ),
        migrations.AddField(
            model_name='faction',
            name='starter_building_types',
            field=models.ManyToManyField(to='maingame.buildingtype'),
        ),
        migrations.AddField(
            model_name='player',
            name='building_types_available',
            field=models.ManyToManyField(to='maingame.buildingtype'),
        ),
    ]
