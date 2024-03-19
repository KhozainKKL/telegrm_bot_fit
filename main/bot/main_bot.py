import datetime

import telebot
from asgiref.sync import sync_to_async
from django.conf import settings
from telebot.async_telebot import AsyncTeleBot

from bot.example_text import helper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import calendar
from bot.middleware import AddNewUserMiddleware
from bot.models import TelegramUser, UserFit

bot = AsyncTeleBot(settings.TG_API_KEY, parse_mode='HTML')
telebot.logger.setLevel(settings.LOGLEVEL)

bot.setup_middleware(AddNewUserMiddleware(bot))


def require_authentication(func):
    async def wrapper(message, *args, **kwargs):
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


@bot.message_handler(commands=['group_lesson'])
@require_authentication
async def send_calendar(message):
    now = datetime.datetime.now()
    month = now.month
    year = now.year

    # Если текущий месяц последний в году, переключаемся на следующий год
    if month == 12:
        year += 1

    markup = InlineKeyboardMarkup(row_width=3)

    # Генерируем кнопки для выбора месяца на русском языке
    russian_month_names = [
        "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
        "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"
    ]
    for i in range(3):
        markup.add(InlineKeyboardButton(text=russian_month_names[(now.month + i - 1) % 12],
                                        callback_data=f"month_{year}_{(month + i - 1) % 12 + 1}"))

    await bot.send_message(message.chat.id, "Выберите месяц:", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'month')
    async def choose_day(call):
        year, month = map(int, call.data.split('_')[1:])
        markup = InlineKeyboardMarkup()

        num_days = calendar.monthrange(year, month)[1]

        days_of_month = [day for day in range(1, num_days + 1)]

        weeks = [days_of_month[i:i + 7] for i in range(0, len(days_of_month), 7)]

        for week in weeks:
            row = []
            for day in week:
                row.append(InlineKeyboardButton(text=str(day), callback_data=f"day_{year}_{month}_{day}"))
            markup.row(*row)

        markup.row(InlineKeyboardButton(text="Назад", callback_data="back_to_month"))

        await bot.edit_message_text(f"Выберите день в {datetime.date(year, month, 1).strftime('%B')}:",
                                    call.message.chat.id, call.message.message_id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'day')
    async def choose_time(call):
        year, month, day = map(int, call.data.split('_')[1:])
        markup = InlineKeyboardMarkup()

        first_half_buttons = []
        for hour in range(10, 15):
            first_half_buttons.extend([
                InlineKeyboardButton(text=f"{hour}:00", callback_data=f"time_{year}_{month}_{day}_{hour}_00"),
            ])

        markup.row(*first_half_buttons)

        second_half_buttons = []
        for hour in range(15, 21):
            second_half_buttons.extend([
                InlineKeyboardButton(text=f"{hour}:00", callback_data=f"time_{year}_{month}_{day}_{hour}_00"),
            ])

        markup.row(*second_half_buttons)

        # Добавляем кнопку "Назад" для возврата к выбору дня
        markup.row(InlineKeyboardButton(text="Назад", callback_data="back_to_month"))

        await bot.edit_message_text(f"Выберите время в {datetime.date(year, month, day).strftime('%d.%m.%Y')}:",
                                    call.message.chat.id, call.message.message_id, reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.split('_')[0] == 'time')
    async def process_choice(call):

        await bot.edit_message_text(f"<b>Вы выбрали дату и время: {'-'.join(call.data.split('_')[1:4])}, "
                                    f"{':'.join(call.data.split('_')[4:6])}</b>\n Ждём Вас на тренировке.",
                                    call.message.chat.id,
                                    call.message.message_id)

        await bot.send_sticker(call.message.chat.id,
                               sticker='CAACAgIAAxkBAAELtpdl9WfB4snERAkVgZOph6nRzVHAYwACqQADFkJrCiSoJ_sldvhYNAQ')

    @bot.callback_query_handler(func=lambda call: call.data == "back_to_month")
    async def back_to_month(call):
        await bot.edit_message_text("Выберите месяц:", call.message.chat.id, call.message.message_id,
                                    reply_markup=markup)


@bot.message_handler(func=lambda message: True)
@require_authentication
async def echo_message(message):
    await bot.send_message(message.chat.id, helper)
