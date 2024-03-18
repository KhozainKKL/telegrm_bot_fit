from django.db import models


# Create your models here.

class TelegramUser(models.Model):
    class Meta:
        verbose_name = 'Пользователь тлеграмма'
        verbose_name_plural = 'Пользователи телеграмма'

    card_id = models.PositiveIntegerField(unique=True, blank=True, null=True, verbose_name='Номер карты', db_index=True)
    telegram_user_id = models.PositiveBigIntegerField(unique=True, blank=True, null=True, db_index=True,
                                                      verbose_name='ID пользователя telegram')
    email = models.EmailField(verbose_name='Почта')
    is_authenticated = models.BooleanField(default=False, verbose_name='Авторизация')
    username = models.CharField(blank=True, null=True, verbose_name='Никнейм')
    first_name = models.CharField(blank=True, null=True, verbose_name='Имя')
    last_name = models.CharField(blank=True, null=True, verbose_name='Фамилия')

    def __str__(self):
        return f'{self.telegram_user_id}'

    # @classmethod
    # def authenticate(cls, card_id, telegram_user_id):
    #     try:
    #         user = cls.objects.get(card_id=card_id)
    #         user, created = cls.objects.update_or_create(telegram_user_id=telegram_user_id,
    #                                                      defaults={'card_id': card_id})
    #         if not created:
    #             user.is_authenticated = True
    #             user.save()
    #         return user
    #     except cls.DoesNotExist:
    #         return None
