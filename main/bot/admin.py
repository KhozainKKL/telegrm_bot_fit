from django.contrib import admin
from django.utils.timezone import localtime

from bot.models import TelegramUser, UserFit, TrainerFit, LessonFit, DateLessonFit, TimeLessonFit

admin.site.register(TelegramUser)
admin.site.register(UserFit)
admin.site.register(TrainerFit)
admin.site.register(LessonFit)
admin.site.register(DateLessonFit)


class TimeLessonFitAdmin(admin.ModelAdmin):
    list_display = ('formatted_time',)

    def formatted_time(self, obj):
        return localtime(obj.time).strftime('%Y-%m-%d %H:%M')


admin.site.register(TimeLessonFit, TimeLessonFitAdmin)
