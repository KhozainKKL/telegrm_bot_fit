import datetime

import aiofiles
import telebot
from asgiref.sync import sync_to_async
from django.conf import settings
from telebot.async_telebot import AsyncTeleBot

from bot.example_text import helper, action
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

import calendar
from bot.middleware import AddNewUserMiddleware
from bot.models import TelegramUser, UserFit, LessonFit, TrainerFit
from main.database.get_data_lesson import get_data_lesson, set_data_user_lesson, get_data_my_lesson
from main_table_admin.models import MONTHS_RU

bot = AsyncTeleBot(settings.TG_API_KEY, parse_mode='HTML')
telebot.logger.setLevel(settings.LOGLEVEL)

bot.setup_middleware(AddNewUserMiddleware(bot))


def require_authentication(func):
    async def wrapper(message, *args, **kwargs):
        if message.from_user.is_bot is True:
            user = await get_telegram_user_sync(message.chat.id)
        else:
            user = await get_telegram_user_sync(message.from_user.id)
        if not user or not user.is_authenticated:
            await bot.send_message(message.chat.id, "Вы не авторизованы.")
        else:
            await func(message, *args, **kwargs)

    return wrapper


@sync_to_async
def get_telegram_user_sync(user_id):
    try:
        user = TelegramUser.objects.get(telegram_user_id=user_id)
        return user
    except TelegramUser.DoesNotExist:
        return None


@bot.message_handler(regexp='Записаться на групповое занятие 🤸‍♂️')
@require_authentication
async def send_calendar(message):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton(text="По виду занятия", callback_data="by_type"),
        InlineKeyboardButton(text="К тренеру", callback_data="by_trainer"),
        InlineKeyboardButton(text="По дате и времени", callback_data="any")
    )
    await bot.send_message(message.chat.id, "Как вы хотите записаться на групповое занятие?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data in ['by_type', 'by_trainer', 'any'])
    async def choose_option(call):
        result = await get_data_lesson(call.data)
        if call.data == "by_type":
            await choose_by_type(call.message, result)
        elif call.data == "by_trainer":
            await choose_by_trainer(call.message, result)
        elif call.data == "any":
            await choose_any(call.message, result)

    async def choose_by_type(message, lesson_types):
        # Получаем все виды занятий из базы данных

        markup = InlineKeyboardMarkup(row_width=1)
        for lesson_type in lesson_types:
            markup.add(InlineKeyboardButton(text=lesson_type, callback_data=f"type_{lesson_type}"))
        markup.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_month"))

        await bot.edit_message_text("Выберите вид занятия:", message.chat.id, message.message_id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('type_'))
    async def handle_lesson_type(call):
        # Получаем выбранный тип занятия из call.data
        lesson_type = call.data.split('_')[1]
        # Получаем даты занятий для выбранного типа занятия
        dates = await get_data_lesson(call.data, data=lesson_type)
        # Отображаем доступные даты занятий
        markup = InlineKeyboardMarkup(row_width=1)
        for date in dates:
            formatted_date = f"{date.strftime('%d')} {MONTHS_RU[date.month]} {date.strftime('%Y')} г. {date.strftime('%H:%M')}"
            markup.add(InlineKeyboardButton(text=str(formatted_date), callback_data=f"date_{date}"))
        markup.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_month"))
        # Отправляем сообщение с выбором даты занятия
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    text="<blockquote>️<i>Если кнопка не активна, то запись "
                                         "на занятие закрыта.</i></blockquote>\n Выберите дату занятия:",
                                    message_id=call.message.message_id, reply_markup=markup)

    async def choose_by_trainer(message, trainers):
        # Получаем всех тренеров из базы данных

        markup = InlineKeyboardMarkup(row_width=1)
        for trainer in trainers:
            if trainer.last_name:
                markup.add(InlineKeyboardButton(text=f"{trainer.first_name} {trainer.last_name}",
                                                callback_data=f"trainer_{trainer.id}"))
            else:
                markup.add(InlineKeyboardButton(text=f"{trainer.first_name}",
                                                callback_data=f"trainer_{trainer.id}"))
        markup.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_month"))

        await bot.edit_message_text("Выберите тренера:", message.chat.id, message.message_id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('trainer_'))
    async def handle_trainer_lesson_type(call):
        # Получаем выбранный тип занятия из call.data
        trainer = call.data.split('_')[1]
        # Получаем даты занятий для выбранного типа занятия
        lesson = await get_data_lesson(call.data, data=trainer)
        # Отображаем доступные даты занятий
        markup = InlineKeyboardMarkup(row_width=1)
        for types in lesson:
            markup.add(InlineKeyboardButton(text=str(types), callback_data=f"trainers_lesson_{types}"))
        markup.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_month"))

        # Отправляем сообщение с выбором даты занятия
        await bot.edit_message_text(chat_id=call.message.chat.id, text="Выберите вид занятия:",
                                    message_id=call.message.message_id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('trainers_lesson_'))
    async def handle_trainer_lesson_date(call):
        # Получаем выбранный тип занятия из call.data
        lesson = call.data.split('_')[2]
        # Получаем даты занятий для выбранного типа занятия
        data = await get_data_lesson(call.data, data=lesson)
        # Отображаем доступные даты занятий
        markup = InlineKeyboardMarkup(row_width=1)
        for types in data:
            formatted_date = f"{types.strftime('%d')} {MONTHS_RU[types.month]} {types.strftime('%Y')} г. {types.strftime('%H:%M')}"
            markup.add(InlineKeyboardButton(text=str(formatted_date), callback_data=f"date_{types}"))
        markup.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_month"))

        # Отправляем сообщение с выбором даты занятия
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    text="<blockquote>️<i>Если кнопка не активна, то запись "
                                         "на занятие закрыта.</i></blockquote>\n Выберите дату занятия:",
                                    message_id=call.message.message_id, reply_markup=markup)

    async def choose_any(message, dates):
        # Получаем все даты занятий из базы данных

        markup = InlineKeyboardMarkup(row_width=1)
        for date in dates:
            formatted_date = f"{date.strftime('%d')} {MONTHS_RU[date.month]} {date.strftime('%Y')} г. {date.strftime('%H:%M')}"
            markup.add(InlineKeyboardButton(text=str(formatted_date), callback_data=f"date_{date}"))
        markup.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_month"))

        await bot.edit_message_text("Выберите дату занятия:", message.chat.id, message.message_id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith('date_'))
    async def handle_date(call):
        date = call.data.split('_')[1]
        await set_data_user_lesson(call, date)
        data = await get_data_lesson(call.data, data=date, message=call)
        # Обработка выбора пользователя по дате
        formatted_date = (f"{data[0].date.strftime('%d')} {MONTHS_RU[data[0].date.month]} "
                          f"{data[0].date.strftime('%Y')} г. {data[0].date.strftime('%H:%M')}")
        await bot.answer_callback_query(call.id, f"Вы записаны к тренеру: {data[0].trainer}\n"
                                                 f"На занятие: {data[0].lesson}\n"
                                                 f" {formatted_date}")
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    text=f"<b>Вы записаны к тренеру: {data[0].trainer}\n"
                                         f"На занятие: {data[0].lesson}\n"
                                         f" {formatted_date}</b>", message_id=call.message.message_id)
        await bot.send_sticker(call.message.chat.id,
                               sticker='CAACAgIAAxkBAAELtpdl9WfB4snERAkVgZOph6nRzVHAYwACqQADFkJrCiSoJ_sldvhYNAQ')
        with open(f'bot/logging/{call.message.chat.id}', 'a+', encoding='utf-8') as file:
            file.write(
                f"[INFO]-[{datetime.datetime.now()}]:Вы записаны к тренеру: {data[0].trainer} - На занятие: {data[0].lesson} - {formatted_date}\n")

    @bot.callback_query_handler(func=lambda call: call.data == "back_to_month")
    async def back_to_month(call):
        await bot.edit_message_text(chat_id=call.message.chat.id, text="Как вы хотите записаться на групповое занятие?",
                                    message_id=call.message.message_id, reply_markup=markup)


@bot.message_handler(regexp='Расписание и описание групповых занятий 🧘‍♂️')
@require_authentication
async def schedule(message):
    sent_message = await bot.send_message(message.chat.id, "Загружаем расписание занятий.")
    file_path = await get_data_lesson(message)
    if not file_path:
        await bot.delete_message(message.chat.id, sent_message.message_id)
        await bot.send_message(message.chat.id, "Расписания еще нет.")
        with open(f'bot/logging/{message.from_user.id}', 'a+', encoding='utf-8') as file:
            file.write(f"[INFO]-[{datetime.datetime.now()}]: Расписания еще нет.\n")
    elif not file_path[1]:
        await bot.delete_message(message.chat.id, sent_message.message_id)
        await bot.send_message(message.chat.id, "Расписания на следующую неделю еще нет.")
        with open(f'bot/logging/{message.from_user.id}', 'a+', encoding='utf-8') as file:
            file.write(f"[INFO]-[{datetime.datetime.now()}]: Расписания на следующую неделю еще нет.\n")
    else:
        for week in file_path:
            async with aiofiles.open(week[0].schedule.path, 'rb') as file:
                # Отправляем документ пользователю
                await bot.send_document(message.chat.id, file)
        with open(f'bot/logging/{message.from_user.id}', 'a+', encoding='utf-8') as file:
            file.write(f"[INFO]-[{datetime.datetime.now()}]:Пользователь запросил расписание занятий на неделю.\n")

        # Удаляем сообщение о начале отправки файла
        await bot.delete_message(message.chat.id, sent_message.message_id)
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton(text="Описание тренировок", callback_data="schedule_")
        )
        await bot.send_message(message.chat.id, "Подробное описание тренировок.", reply_markup=markup)

        @bot.callback_query_handler(func=lambda call: call.data in ['schedule_'])
        async def choose_schedule(call):
            result = await get_data_lesson(call.data)
            keyboard_2 = InlineKeyboardMarkup(row_width=1)
            for lesson_type in result:
                keyboard_2.add(InlineKeyboardButton(text=lesson_type, callback_data=f"schedule_type_{lesson_type}"))

            await bot.edit_message_text("Выберите вид занятия:", call.message.chat.id, call.message.message_id,
                                        reply_markup=keyboard_2)

            @bot.callback_query_handler(func=lambda call: call.data == "back_to_lesson")
            async def back_to_lesson(call):
                await bot.edit_message_text(chat_id=call.message.chat.id,
                                            text="Подробное описание тренировок.",
                                            message_id=call.message.message_id, reply_markup=keyboard_2)

        @bot.callback_query_handler(func=lambda call: call.data.startswith('schedule_type_'))
        async def choose_schedule(call):
            lesson_type = call.data.split('_')[2]
            result = await get_data_lesson(call.data, data=lesson_type)
            print(result)
            keyboard = InlineKeyboardMarkup(row_width=1)
            keyboard.row(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_lesson"))

            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        text=f'<b>Название: {result.title}</b>\n'
                                             f'Описание: {result.description}',
                                        message_id=call.message.message_id, reply_markup=keyboard)


@bot.message_handler(regexp='Занятия на которые Вы записаны📆')
@require_authentication
async def my_lesson(message):
    data = await get_data_my_lesson(message)
    if not data:
        await bot.send_message(message.chat.id, "Вы пока не записаны на занятия.")
    else:
        # Создаем клавиатуру для отображения списка занятий
        keyboard = InlineKeyboardMarkup(row_width=1)
        for user_lesson in data:
            formatted_date = (f"{user_lesson.date.strftime('%d')} "
                              f"{MONTHS_RU[user_lesson.date.month]} {user_lesson.date.strftime('%Y')} г. "
                              f"{user_lesson.date.strftime('%H:%M')}")
            # Формируем название занятия для кнопки
            lesson_title = f"{user_lesson.lesson} - {formatted_date}"
            # Формируем callback_data для кнопки
            callback_data = f"lesson_{user_lesson.pk}"
            # Добавляем кнопку в клавиатуру
            keyboard.add(InlineKeyboardButton(text=lesson_title, callback_data=callback_data))

        # Отправляем сообщение с кнопками списка занятий
        await bot.send_message(message.chat.id, "Список ваших занятий:", reply_markup=keyboard)

    @bot.callback_query_handler(lambda query: query.data.startswith('lesson_'))
    async def lesson_info(query):
        lesson_id = int(query.data.split('_')[1])
        # Получаем информацию о занятии по его ID
        user_lesson = await get_data_my_lesson(query.data, data=lesson_id)
        # Формируем подробную информацию о занятии
        formatted_date = (f"{user_lesson.date.strftime('%d')} "
                          f"{MONTHS_RU[user_lesson.date.month]} {user_lesson.date.strftime('%Y')} г. "
                          f"{user_lesson.date.strftime('%H:%M')}")
        lesson_info_text = (
            f"<b>Занятие:</b> {user_lesson.lesson}\n"
            f"<b>Дата и время:</b> {formatted_date}\n"
            f"<b>Тренер:</b> {user_lesson.trainer.first_name} {user_lesson.trainer.last_name}\n"
        )

        # Создаем клавиатуру для кнопок "Отписаться" и "Назад"
        keyboard_2 = InlineKeyboardMarkup()
        keyboard_2.add(InlineKeyboardButton(text="Отписаться ⛔️", callback_data=f"unsubscribe_{lesson_id}"))
        keyboard_2.add(InlineKeyboardButton(text="Назад ⬅️", callback_data="back_to_lessons"))

        # Отправляем сообщение с подробной информацией о занятии и кнопками
        await bot.edit_message_text(chat_id=query.message.chat.id, text=lesson_info_text,
                                    message_id=query.message.message_id, reply_markup=keyboard_2)

    @bot.callback_query_handler(lambda query: query.data == 'back_to_lessons')
    async def back_to_lessons(query):
        await bot.edit_message_text(chat_id=query.message.chat.id, text="Список ваших занятий:",
                                    message_id=query.message.message_id, reply_markup=keyboard)

    @bot.callback_query_handler(lambda query: query.data.startswith('unsubscribe_'))
    async def unsubscribe_from_lesson(query):
        lesson_id = int(query.data.split('_')[1])
        # Получаем объект занятия, от которого нужно отписаться

        await get_data_my_lesson(query.data, data=lesson_id)

        with open(f'bot/logging/{query.message.chat.id}', 'a+', encoding='utf-8') as file:
            file.write(f"[INFO]-[{datetime.datetime.now()}]:Пользователь отписался от занятия id:{lesson_id}\n")
        # Удаляем запись пользователя о занятии
        await bot.edit_message_text(chat_id=query.message.chat.id, text="Вы успешно отписались от занятия.",
                                    message_id=query.message.message_id)
        # Повторно вызываем функцию отображения списка занятий


@bot.message_handler(func=lambda message: True)
@require_authentication
async def echo_message(message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton('Записаться на групповое занятие 🤸‍♂️'))
    keyboard.add(KeyboardButton('Расписание и описание групповых занятий 🧘‍♂️'))
    keyboard.add(KeyboardButton('Занятия на которые Вы записаны📆'))

    await bot.send_message(message.chat.id, helper, reply_markup=keyboard)
