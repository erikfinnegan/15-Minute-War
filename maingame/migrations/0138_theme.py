# Generated by Django 5.1.1 on 2024-11-24 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maingame', '0137_alter_round_ticks_to_end'),
    ]

    operations = [
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_background', models.CharField(default='#000000', max_length=50)),
                ('base_text', models.CharField(default='#FFFFFF', max_length=50)),
                ('header_background', models.CharField(default='#000000', max_length=50)),
                ('header_text', models.CharField(default='#FFFFFF', max_length=50)),
                ('card_background', models.CharField(default='#000000', max_length=50)),
                ('card_text', models.CharField(default='#FFFFFF', max_length=50)),
            ],
        ),
    ]
