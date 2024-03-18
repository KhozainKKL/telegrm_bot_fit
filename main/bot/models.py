from django.db import models


class TelegramUser(models.Model):
    class Meta:
        verbose_name = 'Пользователь тлеграмма'
        verbose_name_plural = 'Пользователи телеграмма'

    card_id = models.ForeignKey('UserFit', on_delete=models.CASCADE, verbose_name='Номер карты', db_index=True)
    telegram_user_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True, db_index=True,
                                                      verbose_name='ID пользователя telegram')
    email = models.EmailField(verbose_name='Почта')
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

    card = models.PositiveIntegerField(unique=True, blank=True, null=True, verbose_name='Номер карты', db_index=True)
    # fisrt_name =
    # last_name =
    # created_at =
    # created_to =
    # actived =
    # phone =
