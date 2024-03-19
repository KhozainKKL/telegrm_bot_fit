# Generated by Django 4.2.7 on 2024-03-19 05:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserFit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('card', models.PositiveIntegerField(blank=True, db_index=True, null=True, verbose_name='Номер карты')),
                ('first_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='Фамилия')),
                ('created_at', models.DateTimeField(blank=True, null=True, verbose_name='Начало абонемента')),
                ('created_to', models.DateTimeField(blank=True, null=True, verbose_name='Коне абонемента')),
                ('actived', models.BooleanField(default=False, verbose_name='Активен')),
                ('phone', models.CharField(max_length=20, verbose_name='Телефон')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, unique=True, verbose_name='Почта')),
            ],
            options={
                'verbose_name': 'Клиент тренажерного зала',
                'verbose_name_plural': 'Клиенты тренажерного зала',
            },
        ),
        migrations.CreateModel(
            name='TelegramUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('telegram_user_id', models.PositiveBigIntegerField(blank=True, db_index=True, null=True, unique=True, verbose_name='ID пользователя telegram')),
                ('is_authenticated', models.BooleanField(default=False, verbose_name='Авторизация')),
                ('username', models.CharField(blank=True, max_length=20, null=True, verbose_name='Никнейм')),
                ('first_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='Имя')),
                ('last_name', models.CharField(blank=True, max_length=20, null=True, verbose_name='Фамилия')),
                ('card', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='bot.userfit', unique=True, verbose_name='Номер карты')),
            ],
            options={
                'verbose_name': 'Пользователь тлеграмма',
                'verbose_name_plural': 'Пользователи телеграмма',
            },
        ),
    ]
