# Generated by Django 4.2.10 on 2025-07-25 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ressources', '0002_add_new_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ressource',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
    ]
