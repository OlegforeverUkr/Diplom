# Generated by Django 4.2.5 on 2023-09-27 16:20

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('administrators', '0006_alter_session_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='time_start',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
