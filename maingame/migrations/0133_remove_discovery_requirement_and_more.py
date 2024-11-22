# Generated by Django 5.1.1 on 2024-11-22 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0132_dominion_determination'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discovery',
            name='requirement',
        ),
        migrations.AddField(
            model_name='discovery',
            name='other_requirements_dict',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
