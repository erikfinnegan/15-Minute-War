# Generated by Django 5.1.1 on 2024-11-22 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0133_remove_discovery_requirement_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dominion',
            name='acres',
            field=models.IntegerField(default=500),
        ),
    ]
