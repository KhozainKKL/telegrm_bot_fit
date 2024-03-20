import datetime
import logging

from django.utils import timezone
from django.utils.timezone import localtime, utc
from asgiref.sync import sync_to_async
from telebot.types import Chat, User

from bot.models import LessonFit, TrainerFit, TimeLessonFit, TelegramUser, UserFit

logger = logging.getLogger(__name__)


async def get_data_lesson(call, data=None, message=None):
    if call == "by_type":
        result = await sync_to_async(list)(LessonFit.objects.values_list('title', flat=True))
        return result
    elif call == "by_trainer":
        result = await sync_to_async(list)(TrainerFit.objects.all())
        return result
    elif call == "any":
        result = await sync_to_async(list)(TimeLessonFit.objects.values_list('time', flat=True))
        formatted_result = [localtime(time).strftime('%Y-%m-%d %H:%M') for time in result]
        return formatted_result
    elif call.startswith('type_'):
        result = await sync_to_async(list)(
            LessonFit.objects.filter(title=data).values_list('time', flat=True).all())
        result_to = await sync_to_async(list)(
            TimeLessonFit.objects.filter(id__in=result).values_list('time', flat=True))
        formatted_result = [localtime(time).strftime('%Y-%m-%d %H:%M') for time in result_to]
        return formatted_result
    elif call.startswith('trainer_'):
        result = await sync_to_async(list)(TrainerFit.objects.filter(pk=data).values_list('lesson', flat=True).all())
        result_to = await sync_to_async(list)(LessonFit.objects.filter(id__in=result).values_list('title', flat=True))
        return result_to
    elif call.startswith('trainers_lesson_'):
        result_to = await sync_to_async(list)(LessonFit.objects.filter(title=data).values_list('time', flat=True))
        result_to_do = await sync_to_async(list)(
            TimeLessonFit.objects.filter(id__in=result_to).values_list('time', flat=True))
        formatted_result = [localtime(time).strftime('%Y-%m-%d %H:%M') for time in result_to_do]
        return formatted_result

    elif call.startswith('date_'):
        time_naive = datetime.datetime.strptime(data, "%Y-%m-%d %H:%M")
        time_aware = timezone.make_aware(time_naive, timezone.utc) - datetime.timedelta(hours=3)

        tmp = await sync_to_async(list)(TimeLessonFit.objects.filter(time=time_aware))
        related_lessons = await sync_to_async(list)(LessonFit.objects.filter(time__in=tmp))
        related_trainers = await sync_to_async(list)(TrainerFit.objects.filter(lesson__in=related_lessons))

        data = {'lesson': related_lessons, 'trainer': related_trainers}
        return data
