# Generated by Django 5.0.4 on 2024-04-27 20:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_language_book_language'),
    ]

    operations = [
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('oid', models.IntegerField(primary_key=True, serialize=False)),
                ('fname', models.CharField(max_length=20)),
                ('lname', models.CharField(max_length=20)),
                ('price', models.FloatField()),
                ('mail', models.EmailField(max_length=254)),
                ('addr', models.CharField(max_length=50)),
            ],
        ),
    ]
