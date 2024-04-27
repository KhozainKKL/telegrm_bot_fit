import datetime
import json
import logging
import re
from telebot import BaseMiddleware

from django.utils import timezone

from bot.models import TelegramUser, LessonFit, TrainerFit, UserFit, DateLessonFit, MONTHS_RU
from asgiref.sync import sync_to_async
from main_table_admin.models import MainTableAdmin, UserFitLesson
from telebot.types import Chat, User, WebAppInfo, Message
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

logger = logging.getLogger(__name__)


class MainConfigTelegramBot:

    def __init__(self, bot):
        self.bot = bot

    @sync_to_async
    def get_is_authenticated_tg_user(self, message: Chat | Message):
        try:
            get = TelegramUser.objects.get(telegram_user_id=message.from_user.id)
        except TelegramUser.DoesNotExist:
            return 100

    @sync_to_async
    def get_phone_in_user_fit(self, message: list, data: Chat | User):
        try:
            def format_phone_number(phone_number):
                phone_number = str(phone_number)
                digits = re.sub(r'\D', '', phone_number)

                formatted_number = '+7-{}-{}-{}-{}'.format(digits[-10:-7], digits[-7:-4], digits[-4:-2], digits[-2:])
                print(formatted_number)
                return formatted_number

            phone = UserFit.objects.filter(phone=format_phone_number(message))
            print(f'PHONE = {phone}')
            if phone.exists():
                try:
                    data = getattr(data, 'chat')
                except AttributeError:
                    data = data
                first_name = data.first_name
                if not data.first_name:
                    first_name = ''
                last_name = data.last_name
                if not data.last_name:
                    last_name = ''
                username = data.username
                if not data.username:
                    username = ''
                defaults_dict = {'first_name': first_name, 'last_name': last_name, 'username': username}
                set_card = UserFit.objects.get(phone=format_phone_number(message))
                print(f'SET_CARD = {type(set_card)} = {set_card}')
                telegram_user, create_status = TelegramUser.objects.update_or_create(
                    card=set_card,
                    is_authenticated=True,
                    telegram_user_id=data.id,
                    defaults=defaults_dict
                )
                print(f'TELEGRAM_USER = {telegram_user}')
                return True
            else:
                return False
        except UserFit.DoesNotExist:
            return 300

    @sync_to_async
    def get_telegram_user_sync(self, user_id):
        try:
            user = TelegramUser.objects.get(telegram_user_id=user_id)
            return user
        except TelegramUser.DoesNotExist:
            return None

    def require_authentication(self, func: object) -> object:
        async def wrapper(message, *args, **kwargs):
            if message.from_user.is_bot is True:
                user = await self.get_telegram_user_sync(message.chat.id)
            else:
                user = await self.get_telegram_user_sync(message.from_user.id)
            if not user or not user.is_authenticated:
                await self.bot.send_message(message.chat.id, "Вы не авторизованы.")
            else:
                await func(message, *args, **kwargs)

        return wrapper

    @sync_to_async
    def get_data_lesson(self, call, data=None, message=None, relative_user=None):
        current_date = timezone.now().date()
        start_of_week = current_date - datetime.timedelta(days=current_date.weekday())
        end_of_week = start_of_week + datetime.timedelta(days=6)
        if current_date > end_of_week:
            end_date = start_of_week + datetime.timedelta(weeks=1)
        else:
            end_date = start_of_week + datetime.timedelta(weeks=2)
        print(end_date)
        try:
            if call == "by_type" or call == 'schedule_':
                result = list(LessonFit.objects.values_list('title', flat=True))
                return result
            elif call == "by_trainer":
                result = list(TrainerFit.objects.all())
                return result
            elif call == "any":
                result = {'date': list(
                    MainTableAdmin.objects.filter(date__range=[timezone.now(), end_date]).values_list('date',
                                                                                                      flat=True).order_by(
                        'date')),
                    'lesson': list(MainTableAdmin.objects.filter(date__range=[timezone.now(), end_date]))}
                print(result)
                return result
            elif call.startswith('type_'):
                result = list(
                    LessonFit.objects.filter(title=data).values_list('id', flat=True).all())
                result = {'date': list(
                    MainTableAdmin.objects.filter(lesson__in=result,
                                                  date__range=[timezone.now(), end_date]).values_list('date',
                                                                                                      flat=True).order_by(
                        'date')),
                    'lesson': list(
                        MainTableAdmin.objects.filter(lesson__in=result, date__range=[timezone.now(), end_date]))}
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
                    MainTableAdmin.objects.filter(trainer__in=result).values_list('lesson__title',
                                                                                  flat=True).distinct())
                return result_to
            elif call.startswith('trainers_lesson_'):
                result = LessonFit.objects.filter(title=data['lesson']).values_list('id', flat=True).all()
                result_to = {
                    'date': list(MainTableAdmin.objects.filter(trainer=data['trainer_id'], lesson__title=data['lesson'],
                                                               date__range=[timezone.now(), end_date]).values_list(
                        'date',
                        flat=True).order_by('date')),
                    'lesson': list(
                        MainTableAdmin.objects.filter(trainer=data['trainer_id'], lesson__title=data['lesson'],
                                                      date__range=[timezone.now(), end_date]))}
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
                    if file:
                        result.append(file)
                return result

    @sync_to_async
    def set_data_user_lesson(self, message, data, relative_user=None, is_reserve=False):
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
    def get_data_my_lesson(self, query=None, data=None, user_id=None):
        try:
            if query:
                if query.startswith('lesson_'):
                    result = {'lesson': list(MainTableAdmin.objects.filter(pk__in=[data])),
                              'user': UserFitLesson.objects.filter(lesson=data).values_list('is_reserve',
                                                                                            flat=True).first()}
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
                        first_reserve_user_fit_lesson = UserFitLesson.objects.filter(is_reserve=True).order_by(
                            'id').first()
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

    @staticmethod
    def formatted_date(data):
        if isinstance(data, datetime.datetime):
            if not data.hour and not data.minute:
                return f"{data.strftime('%d')} {MONTHS_RU[data.month]} {data.strftime('%Y')} г."
            return f"{data.strftime('%d')} {MONTHS_RU[data.month]} {data.strftime('%Y')} г. {data.strftime('%H:%M')}"
        elif isinstance(data, MainTableAdmin):
            # Предполагаем, что data является экземпляром модели с полем DateField/DateTimeField
            if not data.date.hour and not data.date.minute:
                return f"{data.date.strftime('%d')} {MONTHS_RU[data.date.month]} {data.date.strftime('%Y')} г."
            return f"{data.date.strftime('%d')} {MONTHS_RU[data.date.month]} {data.date.strftime('%Y')} г. {data.date.strftime('%H:%M')}"


class AddNewUserMiddleware(BaseMiddleware):
    def __init__(self, bot: object) -> object:
        super(AddNewUserMiddleware, self).__init__()
        self.bot = bot
        self.card_id_requests = {}
        self.update_types = ['message']

    async def pre_process(self, message, data):
        my_data = None
        try:
            my_data = getattr(message, 'chat')
        except AttributeError:
            pass
        try:
            my_data = getattr(message, 'from_user')
        except AttributeError:
            pass
        if not my_data:
            return None
        if not message.text:
            return None

        if await MainConfigTelegramBot.get_is_authenticated_tg_user(message) == 100:
            markup = ReplyKeyboardMarkup()
            markup.add(KeyboardButton('Поделиться номером телефона ❇️', request_contact=True))
            await self.bot.send_message(message.chat.id,
                                        "Для получения доступа поделитесь своим номером телефона,пожалуйста нажмите кнопку \n"
                                        "<blockquote>️Поделиться номером телефона ❇️</blockquote>\n"
                                        "для своей идентификации в Нашем фитнес-клубе.",
                                        reply_markup=markup)

            @self.bot.message_handler(content_types=['contact'])
            async def web_app(message):
                if message.contact.user_id != message.from_user.id:
                    await self.bot.send_message(message.chat.id, "Номер телефона не действителен.❌\n"
                                                                 "Сработала защита от мошенничества.⤴️")
                else:
                    if not await MainConfigTelegramBot.get_phone_in_user_fit(message=message.contact.phone_number, data=my_data):
                        await self.bot.send_message(message.chat.id, "Вы не были найдены в системе.❌\n"
                                                                     "Уточните свои данные и повторите авторизацию.⤴️")
                    else:
                        await self.bot.send_message(message.chat.id, SampleTextBot.main_text(),
                                                    reply_markup=AllMarkUpForButtonBot.reply_keyboard_button_main())

    async def post_process(self, message, data, exception):
        pass


class AllMarkUpForButtonBot(InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton):

    @staticmethod
    def reply_keyboard_button_main():
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton('Записаться на групповое занятие 🤸‍♂️'))
        keyboard.add(KeyboardButton('Расписание и описание групповых занятий 🧘‍♂️'))
        keyboard.add(KeyboardButton('Занятия на которые Вы записаны📆'))

        return keyboard

    @staticmethod
    def get_main_lesson_all():
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(text="По виду занятия", callback_data="by_type"),
            InlineKeyboardButton(text="К тренеру", callback_data="by_trainer"),
            InlineKeyboardButton(text="По дате и времени", callback_data="any")
        )
        return markup

    @staticmethod
    def back_to_month():
        markup = InlineKeyboardMarkup(row_width=1)
        markup.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_month"))

        return markup

    @staticmethod
    def get_main_lesson_choose_by_type(lesson_types):
        markup = InlineKeyboardMarkup(row_width=1)
        for lesson_type in lesson_types:
            markup.add(InlineKeyboardButton(text=lesson_type, callback_data=f"type_{lesson_type}"))
        markup.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_month"))
        return markup

    @staticmethod
    def get_main_lesson_handle_lesson_type(dates):
        markup = InlineKeyboardMarkup(row_width=1)
        for date in dates:
            formatted_date = MainConfigTelegramBot.formatted_date(date)
            markup.add(InlineKeyboardButton(text=str(formatted_date), callback_data=f"date_{date}"))
        markup.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_month"))
        return markup

    @staticmethod
    def get_main_lesson_choose_by_trainer(trainers):
        markup = InlineKeyboardMarkup(row_width=1)
        for trainer in trainers:
            if trainer.last_name:
                markup.add(InlineKeyboardButton(text=f"{trainer.first_name} {trainer.last_name}",
                                                callback_data=f"trainer_{trainer.id}"))
            else:
                markup.add(InlineKeyboardButton(text=f"{trainer.first_name}",
                                                callback_data=f"trainer_{trainer.id}"))
        markup.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_month"))

        return markup

    @staticmethod
    def get_main_lesson_handle_trainer_lesson_type(lesson, trainer_id):
        markup = InlineKeyboardMarkup(row_width=1)
        for types in lesson:
            markup.add(InlineKeyboardButton(text=str(types), callback_data=f"trainers_lesson_{types}_{trainer_id}"))
        markup.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_month"))

        return markup

    @staticmethod
    def get_main_lesson_handle_date_relative_user(data, date):
        keyboard_relative_user = InlineKeyboardMarkup(row_width=1)
        keyboard_relative_user.add(
            InlineKeyboardButton(text=f'{data["relative_user"].first_name} {data["relative_user"].last_name}',
                                 callback_data=f'date_{date}_{data["relative_user"].pk}'))
        keyboard_relative_user.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_month"))
        return keyboard_relative_user

    @staticmethod
    def button_for_lesson_you_zapis(data, data_2):
        keyboard = InlineKeyboardMarkup(row_width=1)
        for user_lesson in data:
            formatted_date = MainConfigTelegramBot.formatted_date(user_lesson)
            lesson_title = f"{user_lesson.lesson} - {formatted_date}"
            callback_data = f"lesson_{user_lesson.pk}_{data_2}_keyboard"
            keyboard.add(InlineKeyboardButton(text=lesson_title, callback_data=callback_data))

        return keyboard

    @staticmethod
    def button_for_lesson_you_zapis_relative(data, data_2):
        keyboard_2 = InlineKeyboardMarkup(row_width=1)
        for user_lesson in data:
            formatted_date = MainConfigTelegramBot.formatted_date(user_lesson)
            lesson_title = f"{user_lesson.lesson} - {formatted_date}"
            callback_data = f"lesson_{user_lesson.pk}_{data_2.relative_user}_keyboard2"
            keyboard_2.add(InlineKeyboardButton(text=lesson_title, callback_data=callback_data))

        return keyboard_2

    @staticmethod
    def button_for_lesson_you_zapis_unsubscribe(lesson_id, user_id, key):
        keyboard_2 = InlineKeyboardMarkup()
        keyboard_2.add(
            InlineKeyboardButton(text="Отписаться ⛔️", callback_data=f"unsubscribe_{lesson_id}_{user_id}"))
        if key == 'keyboard':
            keyboard_2.add(InlineKeyboardButton(text="Назад ⬅️", callback_data=f"back_to_lessons_user"))
        else:
            keyboard_2.add(InlineKeyboardButton(text="Назад ⬅️", callback_data=f"back_to_lessons_relative_user"))

        return keyboard_2

    @staticmethod
    def button_get_schedule_lesson_group(result=None):
        markup = InlineKeyboardMarkup(row_width=1)
        if not result:
            markup.add(InlineKeyboardButton(text="Описание тренировок", callback_data="schedule_"))
        else:
            for lesson_type in result:
                markup.add(InlineKeyboardButton(text=lesson_type, callback_data=f"schedule_type_{lesson_type}"))

        return markup

    @staticmethod
    def button_back_to_lesson():
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_lesson"))

        return keyboard


class SampleTextBot:

    @staticmethod
    def sticker_true_lesson():
        return 'CAACAgIAAxkBAAELtpdl9WfB4snERAkVgZOph6nRzVHAYwACqQADFkJrCiSoJ_sldvhYNAQ'

    @staticmethod
    def main_text():
        return ('<b>Мы рады Вас приветствовать в фитнес-клубе "LoftGym".</b> 🏋️‍♂️ \n'
                '<em>Для навигации используйте встроенные команды.</em> \n')

    @staticmethod
    def send_promo_users(result):
        formatted_date_at = MainConfigTelegramBot.formatted_date(result['instance']['date_at'])
        formatted_date_to = MainConfigTelegramBot.formatted_date(result['instance']['date_to'])

        return (
            f'<blockquote>️<i>⚠️Просим обратить Ваше внимание!</i>\n '
            f'Только <b>с {formatted_date_at} по {formatted_date_to}</b>\n</blockquote>'
            f'<b>Акция: {result["instance"]["title"]}</b>\n'
            f'<blockquote>{result["instance"]["description"]}</blockquote>\n'
            f'<tg-spoiler><b>Используйте промокод:</b> {result["instance"]["promo"]}</tg-spoiler>'
        )

    @staticmethod
    def canceled_lesson_post_message_users(data):
        formatted_date = MainConfigTelegramBot.formatted_date(data['lesson'][0])
        return (
            f'<blockquote>️<i>⚠️Внимание: Пользовательское оповещение.\n '
            f'<b>Занятие:</b> {data["lesson_title"][0]}\n'
            f'<b>Время:</b> {formatted_date}\n'
            f'<b>ОТМЕНЕНО!*😔 </b></i></blockquote>️'
            f'<b>Причина:</b> {data["lesson"][0].check_canceled_description}\n\n'
            f'<i>*Мы сняли Вашу запись с этого занятия.</i>')

    @staticmethod
    def change_lesson_post_message_users(data):
        formatted_date = MainConfigTelegramBot.formatted_date(data['lesson'][0])
        return (
            f'<blockquote>️<i>⚠️Внимание: Пользовательское оповещение.\n '
            f'<b>Занятие на которое вы были записаны изменено.</b></i></blockquote>️\n '
            f'{data["lesson_title"][0][2]}\n'
            f'<b>Занятие:</b> {data["lesson_title"][0][0]}\n'
            f'<b>Тренер:</b> {data["lesson_title"][0][1]}\n'
            f'<b>Время:</b> {formatted_date}\n'
            f'<i>*Если Вас изменения не устраивают, то отмените свою запись самостоятельно.</i>')

    @staticmethod
    def get_for_user_is_not_reserve(data):
        formatted_date = MainConfigTelegramBot.formatted_date(data['lesson'][0])
        return (
            f'<blockquote>️<i>⚠️Внимание: Пользовательское оповещение. </i></blockquote>️\n '
            f'Вы перенесены с резерва. Можете приходить на:\n'
            f'<b>Занятие:</b> {data["lesson_title"][0]}\n'
            f'<b>Время:</b> {formatted_date}\n')

    @staticmethod
    def user_true_relative_yes():
        return ("<blockquote>️<i>Вы уже записаны на текущее занятие. Вы можете записать "
                "своего родственника, <b>если он является посетителем Нашего фитнес-зала</b>.\n"
                "После его записи ему прейдет уведомление.</i></blockquote>️"
                "Ваш родственник:")

    @staticmethod
    def user_true_relative_none():
        return ("<blockquote>️<i>Вы уже записаны на текущее занятие. Вы можете записать "
                "своего родственника, <b>если он является посетителем Нашего фитнес-клуба</b>.\n"
                "После его записи ему прейдет уведомление.</i></blockquote>️"
                "У Вас нет родственников посещающих Наш фитнес-клуб.")

    @staticmethod
    def user_true_relative_true():
        return ("<blockquote>️<i>Вы уже записаны на текущее занятие. Вы можете записать "
                "своего родственника, <b>если он является посетителем Нашего фитнес-клуба</b>.\n"
                "После его записи ему прейдет уведомление.</i></blockquote>️"
                "Ваш родственник уже записан на это занятие.")

    @staticmethod
    def user_is_reserve():
        return (f'<blockquote>️<i>⚠️Внимание: Пользовательское оповещение.\n'
                f'Слишком много людей хотят попсать на это занятие, но мы Вами дорожим, поэтому:️\n'
                f'Вы записаны в <b>РЕЗЕРВ</b></i></blockquote>\n'
                f'<i>*Если кто-то передумает идти на занятие, то мы Вам сообщим об этом.</i>')

    @staticmethod
    def relative_user_is_reserve():
        return (f'<blockquote>️<i>⚠️Внимание: Пользовательское оповещение.\n'
                f'Слишком много людей хотят попсать на это занятие, но мы Вами дорожим, поэтому:️\n'
                f'Ваш родственник записан в <b>РЕЗЕРВ</b></i></blockquote>\n'
                f'<i>*Если кто-то передумает идти на занятие, то мы Вам или ему сообщим об этом.</i>')
