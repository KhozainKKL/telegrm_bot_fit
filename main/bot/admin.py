from django.contrib import admin
from django.utils.timezone import localtime

from bot.models import TelegramUser, UserFit, TrainerFit, LessonFit, DateLessonFit, TimeLessonFit
from import_export.admin import ImportExportActionModelAdmin
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

admin.site.register(TelegramUser)
admin.site.register(TrainerFit)
admin.site.register(LessonFit)
admin.site.register(DateLessonFit)


class TimeLessonFitAdmin(admin.ModelAdmin):
    list_display = ('formatted_time',)

    def formatted_time(self, obj):
        return localtime(obj.time).strftime('%Y-%m-%d %H:%M')


admin.site.register(TimeLessonFit, TimeLessonFitAdmin)


@admin.register(UserFit)
class UserFitModelAdmin(ImportExportActionModelAdmin):
    pass
