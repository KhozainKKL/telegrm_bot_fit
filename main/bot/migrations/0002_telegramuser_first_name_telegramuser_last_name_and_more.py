# Generated by Django 4.2.7 on 2024-03-18 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='telegramuser',
            name='first_name',
            field=models.CharField(blank=True, null=True, verbose_name='Имя'),
        ),
        migrations.AddField(
            model_name='telegramuser',
            name='last_name',
            field=models.CharField(blank=True, null=True, verbose_name='Фамилия'),
        ),
        migrations.AddField(
            model_name='telegramuser',
            name='username',
            field=models.CharField(blank=True, null=True, verbose_name='Никнейм'),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='card_id',
            field=models.PositiveIntegerField(db_index=True, unique=True, verbose_name='Номер карты'),
        ),
        migrations.AlterField(
            model_name='telegramuser',
            name='telegram_user_id',
            field=models.PositiveBigIntegerField(blank=True, db_index=True, null=True, unique=True, verbose_name='ID пользователя telegram'),
        ),
    ]