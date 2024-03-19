from django.contrib import admin

from bot.models import TelegramUser, UserFit, TrainerFit, LessonFit, DateLessonFit, TimeLessonFit

admin.site.register(TelegramUser)
admin.site.register(UserFit)
admin.site.register(TrainerFit)
admin.site.register(LessonFit)
admin.site.register(DateLessonFit)
admin.site.register(TimeLessonFit)

