# Generated by Django 4.2.7 on 2024-03-25 12:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MainTableAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(blank=True, null=True, verbose_name='Время занятия')),
                ('number_of_recorded', models.PositiveSmallIntegerField(default=0, verbose_name='Количество записанных на занятие')),
                ('check_canceled', models.BooleanField(default=False, verbose_name='Отменить занятие?')),
                ('check_canceled_description', models.CharField(blank=True, max_length=255, null=True, verbose_name='Причина отмены занятия')),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.lessonfit', verbose_name='Занятие')),
                ('trainer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.trainerfit', verbose_name='Тренер')),
                ('week_schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bot.datelessonfit', verbose_name='Недельное расписание')),
            ],
            options={
                'verbose_name': 'Основная информация',
                'verbose_name_plural': 'Основная информация',
            },
        ),
    ]
