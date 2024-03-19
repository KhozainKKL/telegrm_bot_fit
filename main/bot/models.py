from django.db import models


class TelegramUser(models.Model):
    class Meta:
        verbose_name = 'Пользователь тлеграмма'
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
    first_name = models.CharField(max_length=20, blank=True, null=True, verbose_name='Имя')
    last_name = models.CharField(max_length=20, blank=True, null=True, verbose_name='Фамилия')
    created_at = models.DateTimeField(blank=True, null=True, verbose_name='Начало абонемента')
    created_to = models.DateTimeField(blank=True, null=True, verbose_name='Коне абонемента')
    actived = models.BooleanField(default=False, verbose_name='Активен')
    phone = models.IntegerField(verbose_name='Телефон')
    email = models.EmailField(unique=True, blank=True, null=True, verbose_name='Почта')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class TrainerFit(models.Model):
    class Meta:
        verbose_name = 'Тренер тренажерного зала'
        verbose_name_plural = 'Тренеры тренажерного зала'

    first_name = models.CharField(max_length=20, blank=True, null=True, verbose_name='Имя')
    last_name = models.CharField(max_length=20, blank=True, null=True, verbose_name='Фамилия')
    lesson = models.ManyToManyField('LessonFit', blank=True, related_name='trainerfit_lessonfit',
                                    verbose_name='Занятия')

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class LessonFit(models.Model):
    class Meta:
        verbose_name = 'Групповое занятие'
        verbose_name_plural = 'Групповые занятия'

    title = models.CharField(max_length=25, blank=True, null=True, verbose_name='Название')
    description = models.CharField(max_length=255, blank=True, null=True, verbose_name='Описание')
    date_time = models.ManyToManyField('DateLessonFit', blank=True, related_name='lessonfit_datelessonfit',
                                       verbose_name='Промежуточное расписание')
    time = models.ManyToManyField('TimeLessonFit', blank=True, related_name='lessonfit_timelessonfit',
                                  verbose_name='Дата и время занятия')

    def __str__(self):
        return f'{self.title}'


class DateLessonFit(models.Model):
    class Meta:
        verbose_name = 'Расписание группового занятия'
        verbose_name_plural = 'Расписание групповых занятий'

    create_at = models.DateField(verbose_name='Дата начала:')
    create_to = models.DateField(verbose_name='Дата окончания:')

    def __str__(self):
        return f"{self.create_at}: {self.create_to}"


class TimeLessonFit(models.Model):
    class Meta:
        verbose_name = 'Время группового занятия'
        verbose_name_plural = 'Время групповых занятий'

    time = models.DateTimeField(verbose_name='Время занятия')

    def __str__(self):
        return f'{self.time}'



