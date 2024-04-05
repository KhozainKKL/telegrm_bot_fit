from django.contrib import admin

from bot.import_export.resourse import UserFitResource, TrainerFitResource, LessonFitResource
from bot.models import UserFit, TrainerFit, LessonFit, DateLessonFit, TelegramUser
from import_export.admin import ImportExportActionModelAdmin
from django.urls import resolve

admin.site.register(DateLessonFit)
admin.site.register(TelegramUser)


@admin.register(UserFit)
class UserFitModelAdmin(ImportExportActionModelAdmin):
    resource_class = UserFitResource
    search_fields = ['first_name', 'last_name']
    list_display = ['card', 'first_name', 'last_name', 'phone', 'relative_user']
    list_display_links = ['card', 'first_name', 'last_name',]
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

    exclude = ('relative_user',)

    def get_exclude(self, request, obj=None):
        exclude = super().get_exclude(request, obj)
        if obj:
            exclude = tuple(set(exclude) - {'relative_user'})
        return exclude

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "relative_user":
            # Получаем идентификатор объекта из URL
            resolved_url = resolve(request.path_info)
            obj_id = resolved_url.kwargs.get('object_id')
            if obj_id:
                try:
                    # Получаем объект по идентификатору
                    obj = UserFit.objects.get(pk=obj_id)
                    # Исключаем текущий объект из queryset
                    kwargs["queryset"] = UserFit.objects.exclude(id=obj.id)
                except UserFit.DoesNotExist:
                    pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


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