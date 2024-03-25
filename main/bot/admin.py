from django.contrib import admin

from bot.import_export.resourse import UserFitResource, TrainerFitResource, LessonFitResource
from bot.models import UserFit, TrainerFit, LessonFit, DateLessonFit, TelegramUser
from import_export.admin import ImportExportActionModelAdmin

admin.site.register(DateLessonFit)
admin.site.register(TelegramUser)

@admin.register(UserFit)
class UserFitModelAdmin(ImportExportActionModelAdmin):
    resource_class = UserFitResource
    search_fields = ['first_name', 'last_name']
    list_display = ['card', 'first_name', 'last_name', 'phone']


@admin.register(TrainerFit)
class TrainerFitModelAdmin(ImportExportActionModelAdmin):
    resource_class = TrainerFitResource
    search_fields = ['first_name', 'last_name']
    list_display = ['first_name', 'last_name']


@admin.register(LessonFit)
class UserFitModelAdmin(ImportExportActionModelAdmin):
    resource_class = LessonFitResource
    search_fields = ['title']
    list_display = ['title', 'description']
