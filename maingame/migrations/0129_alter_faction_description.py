# Generated by Django 5.1.1 on 2024-11-17 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0128_remove_round_ticks_left_round_ticks_passed_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faction',
            name='description',
            field=models.CharField(blank=True, default='Placeholder description', max_length=1000, null=True),
        ),
    ]
