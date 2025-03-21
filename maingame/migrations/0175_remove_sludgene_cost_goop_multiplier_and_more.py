# Generated by Django 5.1.1 on 2025-02-22 02:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0174_rename_amount_produced_sludgene_amount_secreted_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sludgene',
            name='cost_goop_multiplier',
        ),
        migrations.RemoveField(
            model_name='sludgene',
            name='upkeep_goop_multiplier',
        ),
        migrations.AddField(
            model_name='sludgene',
            name='cost_dict',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='sludgene',
            name='upkeep_dict',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
