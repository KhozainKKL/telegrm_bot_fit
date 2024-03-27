from django.contrib import admin

from .models import UserFitLesson
from main_table_admin.models import MainTableAdmin


@admin.register(MainTableAdmin)
class TrainerFitModelAdmin(admin.ModelAdmin):
    search_fields = ['date', 'lesson', 'week_schedule']
    list_display = ['date', 'lesson', 'trainer', 'number_of_recorded', 'check_canceled',
                    'check_canceled_description']
    list_filter = ('date', 'lesson', 'trainer')
    readonly_fields = ('number_of_recorded',)
    list_display_links = ['date', 'lesson', 'trainer', ]
    # radio_fields = {'trainer': admin.HORIZONTAL}
    autocomplete_fields = ["lesson"]
    fieldsets = [
        (
            "Основная информация",
            {
                "fields": ["date", "lesson", "trainer", "number_of_recorded"],
            },
        ),
        (
            "Отмена занятия",
            {
                "fields": ["check_canceled", "check_canceled_description"],
            },
        ),
    ]


@admin.register(UserFitLesson)
class TrainerFitModelAdmin(admin.ModelAdmin):
    search_fields = ['user', 'lesson']
    list_display = ['user', 'lesson']
    list_filter = ('lesson', 'user')
    list_display_links = ["user", "lesson"]

    fieldsets = [
            (
                "Основная информация",
                {
                    "fields": ["user", "lesson",],
                },
            ),
        ]
