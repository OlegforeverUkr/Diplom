# Generated by Django 4.2.5 on 2023-09-30 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrators', '0013_remove_session_date_end_remove_session_date_start_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='time_end',
            field=models.DateTimeField(default=None),
        ),
    ]
