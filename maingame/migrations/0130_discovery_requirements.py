# Generated by Django 5.1.1 on 2024-11-20 13:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0129_alter_faction_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='discovery',
            name='requirements',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
