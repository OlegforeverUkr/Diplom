# Generated by Django 4.2.5 on 2023-09-27 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrators', '0003_rename_movie_ticket_ticket_movie_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='name_session',
            field=models.CharField(default=None, max_length=100),
        ),
    ]
