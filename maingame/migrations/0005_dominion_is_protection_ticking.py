# Generated by Django 5.1.1 on 2025-07-24 14:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0004_sludgene_is_favorite_alter_dominion_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='dominion',
            name='is_protection_ticking',
            field=models.BooleanField(default=False),
        ),
    ]
