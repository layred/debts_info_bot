# Generated by Django 4.1.7 on 2023-03-09 19:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0003_credit_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='credit',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=7, verbose_name='Сумма на текущий день'),
            preserve_default=False,
        ),
    ]
