# Generated by Django 5.1.1 on 2024-10-10 03:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0086_unit_upkeep_dict'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='incoming_acres_dict',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
