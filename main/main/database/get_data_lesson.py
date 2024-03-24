import datetime
import logging
from django.utils import timezone
from django.utils.timezone import localtime, utc
from asgiref.sync import sync_to_async
from telebot.types import Chat, User

from bot.models import LessonFit, TrainerFit, TimeLessonFit, TelegramUser, UserFit, DateLessonFit, UserFitLesson

logger = logging.getLogger(__name__)


async def get_data_lesson(call, data=None, message=None):
    try:
        if call == "by_type":
            result = await sync_to_async(list)(LessonFit.objects.values_list('title', flat=True))
            return result
        elif call == "by_trainer":
            result = await sync_to_async(list)(TrainerFit.objects.all())
            return result
        elif call == "any":
            result = await sync_to_async(list)(TimeLessonFit.objects.values_list('time', flat=True))
            return result
        elif call.startswith('type_'):
            result = await sync_to_async(list)(
                LessonFit.objects.filter(title=data).values_list('time', flat=True).all())
            result_to = await sync_to_async(list)(
                TimeLessonFit.objects.filter(id__in=result).values_list('time', flat=True))
            return result_to
        elif call.startswith('trainer_'):
            result = await sync_to_async(list)(
                TrainerFit.objects.filter(pk=data).values_list('lesson', flat=True).all())
            result_to = await sync_to_async(list)(
                LessonFit.objects.filter(id__in=result).values_list('title', flat=True))
            return result_to
        elif call.startswith('trainers_lesson_'):
            result_to = await sync_to_async(list)(LessonFit.objects.filter(title=data).values_list('time', flat=True))
            result_to_do = await sync_to_async(list)(
                TimeLessonFit.objects.filter(id__in=result_to).values_list('time', flat=True))
            return result_to_do

        elif call.startswith('date_'):

            tmp = await sync_to_async(list)(TimeLessonFit.objects.filter(time=data))

            related_lessons = await sync_to_async(list)(LessonFit.objects.filter(time__in=tmp))
            related_trainers = await sync_to_async(list)(TrainerFit.objects.filter(lesson__in=related_lessons))

            data = {'lesson': related_lessons, 'trainer': related_trainers}
            return data


    except Exception:
        if call.text == '/schedule':
            today = datetime.date.today()
            start_of_week = today - datetime.timedelta(days=today.weekday())
            end_of_week = start_of_week + datetime.timedelta(days=6)
            next_week_start = end_of_week + datetime.timedelta(days=1)
            next_week_end = next_week_start + datetime.timedelta(days=6)
            week_range_str = next_week_start.strftime('%d.%m') + '-' + next_week_end.strftime('%d.%m')
            file = await sync_to_async(list)(DateLessonFit.objects.filter(schedule__contains=week_range_str))
            return file[0].schedule.path


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
                data = UserFitLesson.objects.select_related('lesson', 'trainer', 'date').get(pk=data)
                return data
            elif query.startswith('unsubscribe_'):
                data = UserFitLesson.objects.get(pk=data)
                data.delete()
    except Exception:
        if query.text == '/my_lesson':
            # Получаем пользователя Telegram
            user_tg = TelegramUser.objects.filter(telegram_user_id=query.from_user.id).values_list('id',
                                                                                                   flat=True).first()
            user_fit = UserFit.objects.get(id=user_tg)
            # Получаем список занятий, на которые записан пользователь
            return list(UserFitLesson.objects.filter(user=user_fit).select_related('lesson', 'date').all())
