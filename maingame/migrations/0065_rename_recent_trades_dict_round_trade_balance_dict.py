# Generated by Django 5.1.1 on 2024-09-30 05:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0064_round_recent_trades_dict'),
    ]

    operations = [
        migrations.RenameField(
            model_name='round',
            old_name='recent_trades_dict',
            new_name='trade_balance_dict',
        ),
    ]
