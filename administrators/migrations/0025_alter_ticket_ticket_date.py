# Generated by Django 4.2.5 on 2023-10-06 10:01

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('administrators', '0024_movie_image_url_alter_ticket_ticket_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='ticket_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
