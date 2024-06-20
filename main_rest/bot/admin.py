from collections import defaultdict
from datetime import timezone, timedelta

from django.contrib import admin, messages

from api.models import MONTHS_RU
from bot.models import UserFitLesson, MainTableAdmin, HallPromo


class UserFitInLines(admin.TabularInline):
    model = UserFitLesson
    autocomplete_fields = ["user"]


@admin.register(MainTableAdmin)
class MainTableModelAdmin(admin.ModelAdmin):
    inlines = [UserFitInLines]
    search_fields = [
        "date",
        "lesson__title",
        "trainer__first_name",
        "trainer__last_name",
    ]
    list_display = [
        "date",
        "lesson",
        "trainer",
        "number_of_recorded",
        "check_canceled",
        "check_canceled_description",
    ]
    list_filter = ("date", "lesson", "trainer")
    readonly_fields = ("number_of_recorded",)
    list_display_links = [
        "date",
        "lesson",
        "trainer",
    ]
    autocomplete_fields = ["lesson", "trainer"]
    list_chart_options = {"aspectRatio": 8}
    # change_form_template = "admin/confirm_save_modal.html"
    ordering = ["date"]
    list_per_page = 50
    fieldsets = [
        (
            "Основная информация",
            {
                "fields": [
                    "date",
                    "lesson",
                    "trainer",
                    ("max_number_of_recorded", "number_of_recorded"),
                ],
            },
        ),
        (
            "ОТМЕНА И ИЗМЕНЕНИЕ",
            {
                "classes": ["collapse", "wide"],
                "fields": [
                    ("check_canceled", "check_canceled_description"),
                    "check_change_description",
                ],
            },
        ),
    ]


@admin.register(UserFitLesson)
class UserFitLessonAdmin(admin.ModelAdmin):
    readonly_fields = ("user", "lesson", "is_reserve", "is_come")


@admin.register(HallPromo)
class HallPromoModelAdmin(admin.ModelAdmin):
    search_fields = ["title", "description"]
    list_display = ["title", "description", "date_at", "date_to", "promo"]
    list_display_links = ["title", "description"]
    fieldsets = [
        (
            "Основная информация",
            {
                "fields": [
                    "title",
                    "description",
                    "date_at",
                    "date_to",
                    "promo",
                    "image",
                ],
            },
        ),
    ]
