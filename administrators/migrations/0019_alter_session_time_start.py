# Generated by Django 4.2.5 on 2023-09-30 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrators', '0018_alter_session_time_start'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='time_start',
            field=models.TimeField(choices=[('10:00', '10:00'), ('12:00', '12:00'), ('14:00', '14:00'), ('16:00', '16:00'), ('18:00', '18:00'), ('20:00', '20:00'), ('22:00', '22:00')], default=None, max_length=5),
        ),
    ]
