# Generated by Django 4.2.5 on 2023-09-27 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administrators', '0004_session_name_session'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='name_session',
            field=models.CharField(default='Название сеанса', max_length=100),
        ),
    ]
