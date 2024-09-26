# Generated by Django 5.1.1 on 2024-09-26 05:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0045_player_timezone'),
    ]

    operations = [
        migrations.AddField(
            model_name='battle',
            name='original_ruler',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='battles_defended', to='maingame.player'),
        ),
    ]
