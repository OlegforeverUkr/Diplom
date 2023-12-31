# Generated by Django 4.2.5 on 2023-09-30 09:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrators', '0012_alter_session_date_end_alter_session_date_start_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='date_end',
        ),
        migrations.RemoveField(
            model_name='session',
            name='date_start',
        ),
        migrations.AddField(
            model_name='session',
            name='date_showing_end',
            field=models.DateField(default=None),
        ),
        migrations.AddField(
            model_name='session',
            name='date_showing_start',
            field=models.DateField(default=None),
        ),
        migrations.AlterField(
            model_name='session',
            name='time_end',
            field=models.DateTimeField(),
        ),
    ]
