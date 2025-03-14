# Generated by Django 5.1.1 on 2024-12-31 03:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0154_dominion_op_quested_alter_dominion_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Artifact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
                ('ruler', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='maingame.dominion')),
            ],
        ),
    ]
