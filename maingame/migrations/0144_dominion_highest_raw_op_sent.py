# Generated by Django 5.1.1 on 2024-11-25 03:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0143_alter_theme_input_background_alter_theme_input_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='dominion',
            name='highest_raw_op_sent',
            field=models.IntegerField(default=0),
        ),
    ]
