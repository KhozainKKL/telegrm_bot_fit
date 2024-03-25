import datetime
import logging
from asgiref.sync import sync_to_async
from bot.models import LessonFit, TrainerFit, TelegramUser, UserFit, DateLessonFit
from main_table_admin.models import UserFitLesson, MainTableAdmin, MONTHS_RU

logger = logging.getLogger(__name__)


@sync_to_async
def get_data_lesson(call, data=None, message=None):
    try:
        if call == "by_type":
            result = list(LessonFit.objects.values_list('title', flat=True))
            return result
        elif call == "by_trainer":
            result = list(TrainerFit.objects.all())
            return result
        elif call == "any":
            result = list(MainTableAdmin.objects.all().values_list('date', flat=True))
            return result
        elif call.startswith('type_') or call.startswith('trainers_lesson_'):
            result = list(
                LessonFit.objects.filter(title=data).values_list('id', flat=True).all())
            result_to = list(
                MainTableAdmin.objects.filter(lesson__in=result).values_list('date', flat=True))
            return result_to
        elif call.startswith('trainer_'):
            result = list(
                TrainerFit.objects.filter(pk=data).values_list('id', flat=True))
            result_to = list(
                MainTableAdmin.objects.filter(trainer__in=result).values_list('lesson__title', flat=True).distinct())
            return result_to
        elif call.startswith('date_'):
            tmp = list(MainTableAdmin.objects.filter(date=data))
            print(tmp)
            return list(tmp)


    except Exception:
        if call.text == '/schedule':
            today = datetime.date.today()
            start_of_week = today - datetime.timedelta(days=today.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)
            next_week_start = end_of_week + datetime.timedelta(days=1)
            next_week_end = next_week_start + datetime.timedelta(days=6)
            week_range_str = next_week_start.strftime('%d.%m') + '-' + next_week_end.strftime('%d.%m')
            file = list(DateLessonFit.objects.filter(schedule__contains=week_range_str))
            return file


@sync_to_async
def set_data_user_lesson(message, data):
    tmp = TimeLessonFit.objects.filter(time=data).first()
    related_lessons = LessonFit.objects.filter(time=tmp).first()
    related_trainers = TrainerFit.objects.filter(lesson=related_lessons).first()
    user_tg = TelegramUser.objects.filter(telegram_user_id=message.from_user.id).values_list('id', flat=True).first()
    user_fit = UserFit.objects.get(id=user_tg)
    result, created = UserFitLesson.objects.get_or_create(user=user_fit, lesson=related_lessons,
                                                          trainer=related_trainers,
                                                          date=tmp)


@sync_to_async
def get_data_my_lesson(query=None, data=None):
    try:
        if query:
            if query.startswith('lesson_'):
                print(data)
                data = list(UserFitLesson.objects.filter(lesson=data).values_list('lesson', flat=True))
                print(data)
                data = list(MainTableAdmin.objects.get(pk=data))
                print(data)
                return data
            elif query.startswith('unsubscribe_'):
                data = list(UserFitLesson.objects.get(pk=data))
                data.delete()
    except Exception:
        if query.text == '/my_lesson':
            # Получаем пользователя Telegram
            user_tg = TelegramUser.objects.filter(telegram_user_id=query.from_user.id).values_list('id',
                                                                                                   flat=True).first()
            user_fit = UserFit.objects.get(id=user_tg)
            # Получаем список занятий, на которые записан пользователь
            data = list(UserFitLesson.objects.filter(user=user_fit).values_list('lesson', flat=True))
            data_to = list(MainTableAdmin.objects.filter(pk__in=data))
            print(data_to)
            return data_to
