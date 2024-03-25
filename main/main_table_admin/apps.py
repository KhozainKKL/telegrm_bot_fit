from django.apps import AppConfig


class MainTableAdminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main_table_admin'
    verbose_name = 'Основная таблица администратора'
