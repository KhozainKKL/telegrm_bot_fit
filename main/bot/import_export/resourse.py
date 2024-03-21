from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from bot.models import UserFit, TrainerFit, LessonFit


class UserFitResource(resources.ModelResource):
    id = fields.Field(column_name='', attribute='id')
    card = fields.Field(column_name='Номер карты', attribute='card')
    first_name = fields.Field(column_name='Имя', attribute='first_name')
    last_name = fields.Field(column_name='Фамилия', attribute='last_name')
    created_at = fields.Field(column_name='Начало абонемента', attribute='created_at')
    created_to = fields.Field(column_name='Конец абонемента', attribute='created_to')
    actived = fields.Field(column_name='Активен', attribute='actived')
    phone = fields.Field(column_name='Номер телефона', attribute='phone')
    email = fields.Field(column_name='email', attribute='email')

    class Meta:
        model = UserFit


class TrainerFitResource(resources.ModelResource):
    id = fields.Field(column_name='', attribute='id')
    first_name = fields.Field(column_name='Имя', attribute='first_name')
    last_name = fields.Field(column_name='Фамилия', attribute='last_name')
    lesson = fields.Field(column_name='Занятия', attribute='lesson', widget=ManyToManyWidget(LessonFit, 'title'))

    class Meta:
        model = TrainerFit
