import datetime
import logging
from asgiref.sync import sync_to_async
from bot.models import LessonFit, TrainerFit, TelegramUser, UserFit, DateLessonFit
from main_table_admin.models import UserFitLesson, MainTableAdmin
from django.utils import timezone

logger = logging.getLogger(__name__)


@sync_to_async
def get_data_lesson(call, data=None, message=None, relative_user=None):
    try:
        if call == "by_type" or call == 'schedule_':
            result = list(LessonFit.objects.values_list('title', flat=True))
            return result
        elif call == "by_trainer":
            result = list(TrainerFit.objects.all())
            return result
        elif call == "any":
            result = {'date': list(
                MainTableAdmin.objects.filter(date__gte=timezone.now()).values_list('date', flat=True)),
                'lesson': list(MainTableAdmin.objects.filter(date__gte=timezone.now()))}
            print(result)
            return result
        elif call.startswith('type_') or call.startswith('trainers_lesson_'):
            result = list(
                LessonFit.objects.filter(title=data).values_list('id', flat=True).all())
            result = {'date': list(
                MainTableAdmin.objects.filter(lesson__in=result, date__gte=timezone.now()).values_list('date',
                                                                                                       flat=True)),
                'lesson': list(MainTableAdmin.objects.filter(lesson__in=result, date__gte=timezone.now()))}
            print(result)
            return result
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
            result = {'state': True, 'tmp': None, 'relative_user': None, 'state_relative_user': True,
                      'is_reserve': False}
            if not relative_user:
                get_card = TelegramUser.objects.get(telegram_user_id=message).card
                get_user = UserFitLesson.objects.filter(user=get_card).values_list('lesson__lesson', flat=True)
                get_user_lesson = list(MainTableAdmin.objects.filter(lesson__in=get_user).filter(date=data))
                result['tmp'] = list(MainTableAdmin.objects.filter(date=data))
                if get_user_lesson == result['tmp']:
                    result['state'] = False
                    result['relative_user'] = get_card.relative_user
                if result['tmp'][0].number_of_recorded >= result['tmp'][0].max_number_of_recorded:
                    result['is_reserve'] = True
                print(result)
                return result
            else:
                get_card = UserFit.objects.get(id=relative_user)
                get_user = UserFitLesson.objects.filter(user=relative_user).values_list('lesson__lesson', flat=True)
                get_user_lesson = list(MainTableAdmin.objects.filter(lesson__in=get_user).filter(date=data))
                result['tmp'] = list(MainTableAdmin.objects.filter(date=data))
                if get_user_lesson == result['tmp']:
                    result['state_relative_user'] = False
                    result['relative_user'] = None
                if result['tmp'][0].number_of_recorded >= result['tmp'][0].max_number_of_recorded:
                    result['is_reserve'] = True
                elif get_user_lesson != result['tmp']:
                    result['relative_user'] = get_card
                print(result)
                return result
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
def set_data_user_lesson(message, data, relative_user=None, is_reserve=False):
    if not is_reserve:
        if not relative_user:
            tmp = MainTableAdmin.objects.filter(date=data).first()
            user_tg = TelegramUser.objects.filter(telegram_user_id=message.from_user.id).values_list('card_id',
                                                                                                     flat=True).first()
            user_fit = UserFit.objects.get(id=user_tg)
            result, created = UserFitLesson.objects.get_or_create(user=user_fit, lesson=tmp)
            tmp.number_of_recorded += 1
            tmp.save()
        elif relative_user:
            tmp = MainTableAdmin.objects.filter(date=data).first()
            user_fit = UserFit.objects.get(id=relative_user)
            result, created = UserFitLesson.objects.get_or_create(user=user_fit, lesson=tmp)
            tmp.number_of_recorded += 1
            tmp.save()
    else:
        if not relative_user:
            tmp = MainTableAdmin.objects.filter(date=data).first()
            user_tg = TelegramUser.objects.filter(telegram_user_id=message.from_user.id).values_list('card_id',
                                                                                                     flat=True).first()
            user_fit = UserFit.objects.get(id=user_tg)
            result, created = UserFitLesson.objects.get_or_create(user=user_fit, lesson=tmp, is_reserve=is_reserve)
            tmp.number_of_recorded += 1
            tmp.save()
        elif relative_user:
            tmp = MainTableAdmin.objects.filter(date=data).first()
            user_fit = UserFit.objects.get(id=relative_user)
            result, created = UserFitLesson.objects.get_or_create(user=user_fit, lesson=tmp, is_reserve=is_reserve)
            tmp.number_of_recorded += 1
            tmp.save()


@sync_to_async
def get_data_my_lesson(query=None, data=None, user_id=None):
    try:
        if query:
            if query.startswith('lesson_'):
                result = {'lesson': list(MainTableAdmin.objects.filter(pk__in=[data])),
                          'user': UserFitLesson.objects.filter(lesson=data).values_list('user', flat=True).first()}
                print(result)
                return result
            elif query.startswith('unsubscribe_'):
                tmp = MainTableAdmin.objects.filter(pk=data).first()
                if tmp.number_of_recorded != 0:
                    tmp.number_of_recorded -= 1
                tmp.save()
                data = UserFitLesson.objects.filter(user__card=int(user_id.split('-')[0]), lesson=data)
                check_is_reserve = data[0].is_reserve
                data[0].delete()
                if tmp.number_of_recorded >= tmp.max_number_of_recorded and not check_is_reserve:
                    first_reserve_user_fit_lesson = UserFitLesson.objects.filter(is_reserve=True).order_by('id').first()
                    first_reserve_user_fit_lesson.is_reserve = False
                    first_reserve_user_fit_lesson.save()

    except Exception:
        if query.text == 'Занятия на которые Вы записаны📆':
            result = {'user': None, 'user_id': None, 'relative_user': None}
            # Получаем пользователя Telegram
            user_tg = TelegramUser.objects.filter(telegram_user_id=query.from_user.id).values_list('card_id',
                                                                                                   flat=True).first()
            result['user_id'] = UserFit.objects.get(id=user_tg)
            # Получаем список занятий, на которые записан пользователь
            data = list(
                UserFitLesson.objects.filter(user=result['user_id'], lesson__date__gte=timezone.now()).values_list(
                    'lesson',
                    flat=True))
            result['user'] = list(MainTableAdmin.objects.filter(pk__in=data))
            relative_ = list(
                UserFitLesson.objects.filter(user=result['user_id'].relative_user,
                                             lesson__date__gte=timezone.now()).values_list(
                    'lesson', flat=True))
            result['relative_user'] = list(MainTableAdmin.objects.filter(pk__in=relative_))
            print(result)
            return result
