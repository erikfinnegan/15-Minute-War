# Generated by Django 5.1.1 on 2024-11-20 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0130_discovery_requirements'),
    ]

    operations = [
        migrations.RenameField(
            model_name='discovery',
            old_name='requirements',
            new_name='required_discoveries',
        ),
        migrations.AddField(
            model_name='discovery',
            name='required_faction_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
