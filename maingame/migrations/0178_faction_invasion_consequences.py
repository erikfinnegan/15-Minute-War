# Generated by Django 5.1.1 on 2025-02-23 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0177_sludgene_discount_percent'),
    ]

    operations = [
        migrations.AddField(
            model_name='faction',
            name='invasion_consequences',
            field=models.CharField(blank=True, max_length=1000, null=True),
        ),
    ]
