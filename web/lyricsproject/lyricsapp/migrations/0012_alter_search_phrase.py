# Generated by Django 5.0.4 on 2024-04-28 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lyricsapp', '0011_alter_search_api_version'),
    ]

    operations = [
        migrations.AlterField(
            model_name='search',
            name='phrase',
            field=models.CharField(max_length=50),
        ),
    ]
