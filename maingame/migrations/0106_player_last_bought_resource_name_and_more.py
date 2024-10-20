# Generated by Django 5.1.1 on 2024-10-20 04:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0105_alter_faction_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='last_bought_resource_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='player',
            name='last_sold_resource_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
