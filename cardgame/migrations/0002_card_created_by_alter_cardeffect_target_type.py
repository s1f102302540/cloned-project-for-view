# Generated by Django 5.1.4 on 2024-12-13 04:51

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cardgame', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardeffect',
            name='target_type',
            field=models.CharField(max_length=100),
        ),
    ]
