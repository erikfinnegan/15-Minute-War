# Generated by Django 5.1.1 on 2024-10-20 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0103_rename_units_involved_dict_battle_units_defending_dict_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='faction',
            name='description',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
