# Generated by Django 5.1.1 on 2024-10-20 03:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0104_faction_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='faction',
            name='description',
            field=models.CharField(blank=True, default='Placeholder description', max_length=500, null=True),
        ),
    ]
