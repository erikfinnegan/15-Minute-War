# Generated by Django 5.1.1 on 2024-09-18 00:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0012_unit_perk_string_unit_quantity_marshaled'),
    ]

    operations = [
        migrations.AddField(
            model_name='terrain',
            name='unit_op_dp_ratio',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='terrain',
            name='unit_perk_options',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
