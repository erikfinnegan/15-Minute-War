# Generated by Django 5.1.1 on 2024-10-10 04:07

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0087_player_incoming_acres_dict'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='battle',
            name='attackers',
        ),
        migrations.RemoveField(
            model_name='battle',
            name='original_ruler',
        ),
        migrations.AddField(
            model_name='battle',
            name='acres_conquered',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='battle',
            name='attacker',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='battles_attacked', to='maingame.player'),
        ),
        migrations.AddField(
            model_name='battle',
            name='defender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='battles_defended', to='maingame.player'),
        ),
        migrations.AddField(
            model_name='battle',
            name='op',
            field=models.IntegerField(default=0),
        ),
    ]
