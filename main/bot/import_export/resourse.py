from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget, ManyToManyWidget

from bot.models import UserFit, TrainerFit, LessonFit


class UserFitResource(resources.ModelResource):
    id = fields.Field(column_name='', attribute='id')
    card = fields.Field(column_name='Номер карты', attribute='card')
    first_name = fields.Field(column_name='Имя', attribute='first_name')
    last_name = fields.Field(column_name='Фамилия', attribute='last_name')
    phone = fields.Field(column_name='Номер телефона', attribute='phone')

    class Meta:
        model = UserFit


class TrainerFitResource(resources.ModelResource):
    id = fields.Field(column_name='', attribute='id')
    first_name = fields.Field(column_name='Имя', attribute='first_name')
    last_name = fields.Field(column_name='Фамилия', attribute='last_name')

    class Meta:
        model = TrainerFit


class LessonFitResource(resources.ModelResource):
    id = fields.Field(column_name='', attribute='id')
    title = fields.Field(column_name='Название', attribute='title')
    description = fields.Field(column_name='Описание', attribute='description')

    class Meta:
        model = LessonFit
