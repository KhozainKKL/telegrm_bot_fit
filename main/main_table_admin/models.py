from django.core.exceptions import ValidationError
from django.db import models
from model_utils import FieldTracker
from bot.models import TrainerFit, DateLessonFit, LessonFit, UserFit

MONTHS_RU = {
    1: 'Января', 2: 'Февраля', 3: 'Марта', 4: 'Апреля',
    5: 'Мая', 6: 'Июня', 7: 'Июля', 8: 'Августа',
    9: 'Сентября', 10: 'Октября', 11: 'Ноября', 12: 'Декабря',
}


class MainTableAdmin(models.Model):
    class Meta:
        verbose_name = 'Основная информация'
        verbose_name_plural = 'Основная информация'

    date = models.DateTimeField(blank=True, null=True, verbose_name='Дата и время занятия')
    lesson = models.ForeignKey(LessonFit, on_delete=models.CASCADE, verbose_name='Занятие')
    trainer = models.ForeignKey(TrainerFit, on_delete=models.CASCADE, verbose_name='Тренер')
    week_schedule = models.ForeignKey(DateLessonFit, on_delete=models.CASCADE, verbose_name='Недельное расписание')
    number_of_recorded = models.PositiveSmallIntegerField(default=0, verbose_name='Количество записанных на занятие')
    max_number_of_recorded = models.PositiveSmallIntegerField(default=10, verbose_name='Макс. органичение по записи')
    check_canceled = models.BooleanField(default=False, verbose_name='Отменить занятие?')
    check_canceled_description = models.CharField(max_length=255, blank=True, null=True,
                                                  verbose_name='Причина отмены занятия')
    check_change_description = models.CharField(max_length=255, blank=True, null=True,
                                                verbose_name='Причина изменения занятия')

    tracker = FieldTracker(fields=['date', 'lesson', 'trainer'])

    def clean(self):
        if self.check_canceled and not self.check_canceled_description:
            raise ValidationError(
                {'check_canceled_description': 'Причина отмены занятия обязательна, если занятие отменено.'})
        if not self.check_canceled and self.tracker.changed() and not self.check_change_description:
            raise ValidationError(
                {
                    'check_change_description': 'Причина изменения занятия обязательна, если данные (тренер, занятие или дата) изменены.'}
            )

    def save(self, *args, **kwargs):
        self.full_clean()  # Вызываем метод clean перед сохранением
        super().save(*args, **kwargs)

    def __str__(self):
        formatted_date = f"{self.date.strftime('%d')} {MONTHS_RU[self.date.month]} {self.date.strftime('%Y')} г."
        return f'[{formatted_date}]-{self.lesson}-({self.trainer})'


class UserFitLesson(models.Model):
    class Meta:
        verbose_name = 'Клиент записанный на занятие'
        verbose_name_plural = 'Клиенты записанные на занятия'

    user = models.ForeignKey(UserFit, on_delete=models.CASCADE, verbose_name='Клиент')
    lesson = models.ForeignKey(MainTableAdmin, on_delete=models.CASCADE, verbose_name='Занятие')
    is_reserve = models.BooleanField(default=False, verbose_name='Резервный клиент')

    def __str__(self):
        return f'{self.user}'


class HallPromo(models.Model):
    class Meta:
        verbose_name = 'Акция'
        verbose_name_plural = 'Акции'

    title = models.CharField(max_length=50, verbose_name='Название')
    description = models.CharField(max_length=255, verbose_name='Описание')
    date_at = models.DateField(verbose_name='Начало акции')
    date_to = models.DateField(verbose_name='Конец акции')
    promo = models.CharField(max_length=5, verbose_name='Промокод')
    image = models.ImageField(null=True, upload_to='bot/', verbose_name='фото')

    def __str__(self):
        return f'{self.title}'
