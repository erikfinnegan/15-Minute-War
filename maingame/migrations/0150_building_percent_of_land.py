# Generated by Django 5.1.1 on 2024-12-04 03:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0149_alter_usersettings_juicy_target_threshold'),
    ]

    operations = [
        migrations.AddField(
            model_name='building',
            name='percent_of_land',
            field=models.IntegerField(default=0),
        ),
    ]
