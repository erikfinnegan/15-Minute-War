# Generated by Django 5.1.1 on 2024-10-21 04:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0112_alter_round_has_started'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='use_am_pm',
            field=models.BooleanField(default=True),
        ),
    ]
