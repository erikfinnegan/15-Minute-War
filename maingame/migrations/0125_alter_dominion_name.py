# Generated by Django 5.1.1 on 2024-11-11 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0124_discovery_not_for_factions_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dominion',
            name='name',
            field=models.CharField(blank=True, max_length=30, null=True, unique=True),
        ),
    ]
