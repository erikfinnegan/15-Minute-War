# Generated by Django 5.1.1 on 2025-02-16 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0170_round_bugs'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='has_bugs',
            field=models.BooleanField(default=False),
        ),
    ]
