# Generated by Django 4.1.7 on 2023-03-09 19:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_alter_telegramuser_options_and_more'),
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditor',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='bot.telegramuser', verbose_name='Пользователь телеграмма'),
            preserve_default=False,
        ),
    ]
