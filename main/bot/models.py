import os

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

MONTHS_RU = {
    1: 'Января', 2: 'Февраля', 3: 'Марта', 4: 'Апреля',
    5: 'Мая', 6: 'Июня', 7: 'Июля', 8: 'Августа',
    9: 'Сентября', 10: 'Октября', 11: 'Ноября', 12: 'Декабря',
}


class TelegramUser(models.Model):
    class Meta:
        verbose_name = 'Пользователь телеграмма'
        verbose_name_plural = 'Пользователи телеграмма'

    card = models.OneToOneField('UserFit', on_delete=models.CASCADE, unique=True, blank=True, null=True,
                                verbose_name='Номер карты', db_index=True)
    telegram_user_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True, db_index=True,
                                                      verbose_name='ID пользователя telegram')
    is_authenticated = models.BooleanField(default=False, verbose_name='Авторизация')
    username = models.CharField(max_length=20, blank=True, null=True, verbose_name='Никнейм')
    first_name = models.CharField(max_length=20, blank=True, null=True, verbose_name='Имя')
    last_name = models.CharField(max_length=20, blank=True, null=True, verbose_name='Фамилия')

    def __str__(self):
        return f'{self.telegram_user_id}'


class UserFit(models.Model):
    class Meta:
        verbose_name = 'Клиент тренажерного зала'
        verbose_name_plural = 'Клиенты тренажерного зала'

    card = models.PositiveIntegerField(blank=True, null=True, verbose_name='Номер карты', db_index=True)
    first_name = models.CharField(max_length=20, blank=True, null=True, verbose_name='Имя', db_index=True)
    last_name = models.CharField(max_length=20, blank=True, null=True, verbose_name='Фамилия', db_index=True)
    phone = models.CharField(max_length=16, verbose_name='Телефон',
                             validators=[RegexValidator(regex=r'^\+7-\d{3}-\d{3}-\d{2}-\d{2}$',
                                                        message='Телефонный номер должен быть '
                                                                'в формате +7-999-999-99-99'), ])
    relative_user = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE,
                                      verbose_name='Родственник')

    def __str__(self):
        return f'{self.card}-[{self.first_name} {self.last_name}]'


class TrainerFit(models.Model):
    class Meta:
        verbose_name = 'Тренер тренажерного зала'
        verbose_name_plural = 'Тренеры тренажерного зала'

    first_name = models.CharField(max_length=20, blank=True, null=True, verbose_name='Имя')
    last_name = models.CharField(max_length=20, blank=True, null=True, verbose_name='Фамилия')

    def __str__(self):
        if self.last_name is None:
            return f'{self.first_name}'
        else:
            return f'{self.first_name} {self.last_name}'


class LessonFit(models.Model):
    class Meta:
        verbose_name = 'Групповое занятие'
        verbose_name_plural = 'Групповые занятия'

    title = models.CharField(max_length=25, blank=True, null=True, verbose_name='Название', db_index=True)
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name='Описание')

    def __str__(self):
        return f'{self.title}'


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Не поддерживаемый тип файла.')


class ImageOrDocumentField(models.FileField):
    def __init__(self, *args, **kwargs):
        super(ImageOrDocumentField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ImageOrDocumentField, self).clean(*args, **kwargs)
        validate_file_extension(data)
        return data


class DateLessonFit(models.Model):
    class Meta:
        verbose_name = 'Недельное расписание группового занятия'
        verbose_name_plural = 'Недельные расписания групповых занятий'

    create_at = models.DateField(verbose_name='Дата начала:')
    create_to = models.DateField(verbose_name='Дата окончания:')
    schedule = ImageOrDocumentField(upload_to='bot/lesson_schedule/', verbose_name='Расписание')

    def __str__(self):
        formatted_date_at = f"{self.create_at.strftime('%d')} {MONTHS_RU[self.create_at.month]} {self.create_at.strftime('%Y')} г."
        formatted_date_to = f"{self.create_to.strftime('%d')} {MONTHS_RU[self.create_to.month]} {self.create_to.strftime('%Y')} г."
        return f"{formatted_date_at} - {formatted_date_to}"
