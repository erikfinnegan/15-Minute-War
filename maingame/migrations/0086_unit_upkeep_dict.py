# Generated by Django 5.1.1 on 2024-10-10 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0085_round_base_price_dict'),
    ]

    operations = [
        migrations.AddField(
            model_name='unit',
            name='upkeep_dict',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
