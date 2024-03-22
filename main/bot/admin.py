from django.contrib import admin

from bot.import_export.resourse import UserFitResource, TrainerFitResource
from bot.models import TelegramUser, UserFit, TrainerFit, LessonFit, DateLessonFit, TimeLessonFit, UserFitLesson
from import_export.admin import ImportExportActionModelAdmin

admin.site.register(TelegramUser)
admin.site.register(LessonFit)
admin.site.register(DateLessonFit)
admin.site.register(TimeLessonFit)

@admin.register(UserFit)
class UserFitModelAdmin(ImportExportActionModelAdmin):
    resource_class = UserFitResource
    search_fields = ['first_name', 'last_name']
    list_display = ['card', 'first_name', 'last_name', 'actived', 'phone']
    list_filter = ('actived',)


@admin.register(TrainerFit)
class TrainerFitModelAdmin(ImportExportActionModelAdmin):
    resource_class = TrainerFitResource
    search_fields = ['first_name', 'last_name', 'lesson']
    list_display = ['first_name', 'last_name']


@admin.register(UserFitLesson)
class TrainerFitModelAdmin(admin.ModelAdmin):
    search_fields = ['user', 'lesson', 'trainer', 'date']
    list_display = ['user', 'lesson', 'trainer', 'date']
