# Generated by Django 5.1.1 on 2024-09-19 01:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0019_remove_unit_quantity_in_region_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='associated_deity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='maingame.deity'),
        ),
    ]
