# Generated by Django 5.0.3 on 2024-04-07 01:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lyricsapp', '0007_alter_search_options_remove_search_timestamp_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='search',
            old_name='end_timestamp',
            new_name='done_timestamp',
        ),
    ]
