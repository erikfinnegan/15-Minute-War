# Generated by Django 5.1.1 on 2024-10-19 19:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0102_player_learned_discoveries'),
    ]

    operations = [
        migrations.RenameField(
            model_name='battle',
            old_name='units_involved_dict',
            new_name='units_defending_dict',
        ),
        migrations.AddField(
            model_name='battle',
            name='units_sent_dict',
            field=models.JSONField(blank=True, default=dict, null=True),
        ),
    ]
