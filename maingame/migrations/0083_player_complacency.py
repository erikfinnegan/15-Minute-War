# Generated by Django 5.1.1 on 2024-10-09 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0082_unit_training_dict_alter_player_upgrade_cost_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='complacency',
            field=models.IntegerField(default=0),
        ),
    ]
