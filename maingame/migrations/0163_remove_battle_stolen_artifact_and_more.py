# Generated by Django 5.1.1 on 2025-02-15 20:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0162_remove_dominion_op_quested_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='battle',
            name='stolen_artifact',
        ),
        migrations.RemoveField(
            model_name='battle',
            name='artifact_roll_string',
        ),
        migrations.CreateModel(
            name='MechModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('version', models.IntegerField(default=0)),
                ('capacity', models.IntegerField(default=1)),
                ('base_power', models.IntegerField(default=0)),
                ('base_upgrade_cost_dict', models.JSONField(blank=True, default=dict)),
                ('base_repair_cost_dict', models.JSONField(blank=True, default=dict)),
                ('perk_dict', models.JSONField(blank=True, default=dict)),
                ('durability_current', models.IntegerField(default=100)),
                ('durability_max', models.IntegerField(default=100)),
                ('fragility', models.IntegerField(default=20)),
                ('faction', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='maingame.faction')),
                ('ruler', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='maingame.dominion')),
            ],
        ),
        migrations.DeleteModel(
            name='Artifact',
        ),
    ]
