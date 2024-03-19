from django.db import models


class TelegramUser(models.Model):
    class Meta:
        verbose_name = 'Пользователь тлеграмма'
        verbose_name_plural = 'Пользователи телеграмма'

    card = models.ForeignKey('UserFit', on_delete=models.CASCADE, unique=True, blank=True, null=True,
                             verbose_name='Номер карты', db_index=True)
    telegram_user_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True, db_index=True,
                                                      verbose_name='ID пользователя telegram')
    is_authenticated = models.BooleanField(default=False, verbose_name='Авторизация')
    username = models.CharField(blank=True, null=True, verbose_name='Никнейм')
    first_name = models.CharField(blank=True, null=True, verbose_name='Имя')
    last_name = models.CharField(blank=True, null=True, verbose_name='Фамилия')

    def __str__(self):
        return f'{self.telegram_user_id}'


class UserFit(models.Model):
    class Meta:
        verbose_name = 'Клиент тренажерного зала'
        verbose_name_plural = 'Клиенты тренажерного зала'

    card = models.PositiveIntegerField(blank=True, null=True, verbose_name='Номер карты', db_index=True)
    first_name = models.CharField(blank=True, null=True, verbose_name='Имя')
    last_name = models.CharField(blank=True, null=True, verbose_name='Фамилия')
    created_at = models.DateTimeField(blank=True, null=True, verbose_name='Начало абонемента')
    created_to = models.DateTimeField(blank=True, null=True, verbose_name='Коне абонемента')
    actived = models.BooleanField(default=False, verbose_name='Активен')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name='Почта')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
