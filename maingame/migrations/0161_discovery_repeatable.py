# Generated by Django 5.1.1 on 2025-02-10 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0160_building_is_upgradable'),
    ]

    operations = [
        migrations.AddField(
            model_name='discovery',
            name='repeatable',
            field=models.BooleanField(default=False),
        ),
    ]
