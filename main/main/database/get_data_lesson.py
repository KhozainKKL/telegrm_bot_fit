import datetime
import logging
from asgiref.sync import sync_to_async
from bot.models import LessonFit, TrainerFit, TelegramUser, UserFit, DateLessonFit
from main_table_admin.models import UserFitLesson, MainTableAdmin, MONTHS_RU

logger = logging.getLogger(__name__)


@sync_to_async
def get_data_lesson(call, data=None, message=None):
    try:
        if call == "by_type" or call == 'schedule_':
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
        elif call.startswith('schedule_type_'):
            result = list(
                LessonFit.objects.filter(title=data))
            return result[0]
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
        if call.text == 'Расписание и описание групповых занятий 🧘‍♂️':
            result = []

            today = datetime.date.today()
            start_of_week = today - datetime.timedelta(days=today.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)
            next_week_start = end_of_week + datetime.timedelta(days=1)
            next_week_end = next_week_start + datetime.timedelta(days=6)
            week_range_str = [start_of_week.strftime('%d.%m') + '-' + end_of_week.strftime('%d.%m'),
                              next_week_start.strftime('%d.%m') + '-' + next_week_end.strftime('%d.%m')]
            for week in week_range_str:
                file = list(DateLessonFit.objects.filter(schedule__contains=week))
                result.append(file)
            return result


@sync_to_async
def set_data_user_lesson(message, data):
    tmp = MainTableAdmin.objects.filter(date=data).first()
    user_tg = TelegramUser.objects.filter(telegram_user_id=message.from_user.id).values_list('id', flat=True).first()
    user_fit = UserFit.objects.get(id=user_tg)
    result, created = UserFitLesson.objects.get_or_create(user=user_fit, lesson=tmp)
    tmp.number_of_recorded += 1
    tmp.save()


@sync_to_async
def get_data_my_lesson(query=None, data=None):
    try:
        if query:
            if query.startswith('lesson_'):
                data = list(MainTableAdmin.objects.filter(pk__in=[data]))
                print(data)
                return data[0]
            elif query.startswith('unsubscribe_'):
                tmp = MainTableAdmin.objects.filter(pk=data).first()
                tmp.number_of_recorded -= 1
                tmp.save()
                data = UserFitLesson.objects.filter(lesson=data)
                data[0].delete()
    except Exception:
        if query.text == 'Занятия на которые Вы записаны📆':
            # Получаем пользователя Telegram
            user_tg = TelegramUser.objects.filter(telegram_user_id=query.from_user.id).values_list('id',
                                                                                                   flat=True).first()
            user_fit = UserFit.objects.get(id=user_tg)
            # Получаем список занятий, на которые записан пользователь
            data = list(UserFitLesson.objects.filter(user=user_fit).values_list('lesson', flat=True))
            data_to = list(MainTableAdmin.objects.filter(pk__in=data))
            print(data_to)
            return data_to
