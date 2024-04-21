from django.core.exceptions import ObjectDoesNotExist
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget

from bot.models import UserFit, TrainerFit, LessonFit
from main.settings import logger
from main_table_admin.models import MainTableAdmin, UserFitLesson


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


class MainTableAdminResource(resources.ModelResource):
    date = fields.Field(column_name='Дата', attribute='lesson', widget=ForeignKeyWidget(MainTableAdmin, 'date'))
    lesson = fields.Field(column_name='Занятие', attribute='lesson',
                          widget=ForeignKeyWidget(MainTableAdmin, 'lesson__title'))
    trainer = fields.Field(column_name='Тренер', attribute='lesson',
                           widget=ForeignKeyWidget(MainTableAdmin, 'trainer__first_name'))
    user_card = fields.Field(column_name='Карта', attribute='user', widget=ForeignKeyWidget(UserFit, 'card'))
    user_first_name = fields.Field(column_name='Имя', attribute='user',
                                   widget=ForeignKeyWidget(UserFit, 'first_name'))
    user_last_name = fields.Field(column_name='Фамилия', attribute='user',
                                  widget=ForeignKeyWidget(UserFit, 'last_name'))

    class Meta:
        model = UserFitLesson
        exclude = ('id', 'is_reserve', 'is_come', 'user')
