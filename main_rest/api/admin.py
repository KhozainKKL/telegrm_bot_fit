from django.contrib import admin

from api.models import TelegramUser, UserFit, TrainerFit, LessonFit
from bot.models import UserFitLesson


@admin.register(TelegramUser)
class TelegramUserModelAdmin(admin.ModelAdmin):
    list_display = ["card", "telegram_user_id", "first_name", "last_name"]
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "card",
                    "telegram_user_id",
                    "is_authenticated",
                    "username",
                    "first_name",
                    "last_name",
                ],
            },
        ),
    ]


class MainTableInline(admin.TabularInline):
    model = UserFitLesson


@admin.register(UserFit)
class UserFitModelAdmin(admin.ModelAdmin):
    inlines = [MainTableInline]
    search_fields = ["first_name", "last_name"]
    list_display = ["card", "first_name", "last_name", "phone", "relative_user"]
    list_display_links = [
        "card",
        "first_name",
        "last_name",
    ]
    autocomplete_fields = ["relative_user"]
    fieldsets = [
        (
            "Основная информация",
            {
                "fields": [
                    "card",
                    "first_name",
                    "last_name",
                    "phone",
                ],
            },
        ),
        (
            "Родственник",
            {
                "fields": [
                    "relative_user",
                ],
            },
        ),
    ]


@admin.register(TrainerFit)
class TrainerFitModelAdmin(admin.ModelAdmin):
    search_fields = ["first_name", "last_name"]
    list_display = ["first_name", "last_name"]

    fieldsets = [
        (
            "Основная информация",
            {
                "fields": [
                    "first_name",
                    "last_name",
                ],
            },
        ),
    ]


@admin.register(LessonFit)
class UserFitModelAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    list_display = ["title", "description"]

    fieldsets = [
        (
            "Основная информация",
            {
                "fields": [
                    "title",
                    "description",
                ],
            },
        ),
    ]
