# Generated by Django 5.1.1 on 2024-11-24 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0135_discovery_required_perk_dict_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='discovery',
            name='required_discoveries_or',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
