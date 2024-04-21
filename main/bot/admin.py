from django.contrib import admin

from bot.forms import UserFitModelForm
from bot.import_export.resourse import UserFitResource, TrainerFitResource, LessonFitResource
from bot.models import UserFit, TrainerFit, LessonFit, DateLessonFit, TelegramUser
from import_export.admin import ImportExportActionModelAdmin

from main_table_admin.models import UserFitLesson

admin.site.register(DateLessonFit)
admin.site.register(TelegramUser)


class MainTableInline(admin.TabularInline):
    model = UserFitLesson


@admin.register(UserFit)
class UserFitModelAdmin(ImportExportActionModelAdmin):
    inlines = [MainTableInline]
    resource_class = UserFitResource
    search_fields = ['first_name', 'last_name']
    list_display = ['card', 'first_name', 'last_name', 'phone', 'relative_user']
    list_display_links = ['card', 'first_name', 'last_name', ]
    autocomplete_fields = ['relative_user']
    form = UserFitModelForm
    fieldsets = [
        (
            "Основная информация",
            {
                "fields": ["card", "first_name", "last_name", "phone", ],
            },
        ),
        (
            "Родственник",
            {
                "fields": ["relative_user", ],
            },
        ),
    ]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:
            form.base_fields['relative_user'].widget.attrs['disabled'] = True
        return form


@admin.register(TrainerFit)
class TrainerFitModelAdmin(ImportExportActionModelAdmin):
    resource_class = TrainerFitResource
    search_fields = ['first_name', 'last_name']
    list_display = ['first_name', 'last_name']

    fieldsets = [
        (
            "Основная информация",
            {
                "fields": ["first_name", "last_name", ],
            },
        ),
    ]


@admin.register(LessonFit)
class UserFitModelAdmin(ImportExportActionModelAdmin):
    resource_class = LessonFitResource
    search_fields = ['title']
    list_display = ['title', 'description']

    fieldsets = [
        (
            "Основная информация",
            {
                "fields": ["title", "description", ],
            },
        ),
    ]
