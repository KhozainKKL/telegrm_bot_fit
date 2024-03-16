import datetime

import telebot
from django.conf import settings
from telebot.async_telebot import AsyncTeleBot
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from bot.example_text import helper

bot = AsyncTeleBot(settings.TG_API_KEY, parse_mode='HTML')
telebot.logger.setLevel(settings.LOGLEVEL)


@bot.message_handler(commands=['start'])
async def calendar(message):
    calendar, step = DetailedTelegramCalendar().build()
    await bot.send_message(message.chat.id,
                           f"Select {LSTEP[step]}",
                           reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
async def cal(c):
    result, key, step = DetailedTelegramCalendar().process(c.data)
    if not result and key:
        await bot.edit_message_text(f"Select {LSTEP[step]}",
                                    c.message.chat.id,
                                    c.message.message_id,
                                    reply_markup=key)
    elif result:
        now = datetime.date.today()
        then = datetime.datetime.strftime(result, '%Y-%m-%d')

        if now.month == 12:
            if int(then.split('-')[1]) >= now.month - 9:
                await bot.edit_message_text(f"Вы выбрали: {result}",
                                            c.message.chat.id,
                                            c.message.message_id)
            else:
                await bot.edit_message_text(f'Запись ведется только на первые 3 месяца следующего года.',
                                            c.message.chat.id,
                                            c.message.message_id)

        elif int(then.split('-')[1]) >= now.month + 3 or not int(then.split('-')[0]) == now.year or (
                int(then.split('-')[1]) < now.month or int(then.split('-')[0]) < now.year):
            await bot.edit_message_text(f'Запись ведется только на 3 месяца до конца текущего года.',
                                        c.message.chat.id,
                                        c.message.message_id)
        else:
            await bot.edit_message_text(f"Вы выбрали: {result}",
                                        c.message.chat.id,
                                        c.message.message_id)
            await bot.send_sticker(c.message.chat.id,
                                   sticker='CAACAgIAAxkBAAELtpdl9WfB4snERAkVgZOph6nRzVHAYwACqQADFkJrCiSoJ_sldvhYNAQ')


@bot.message_handler(func=lambda message: True)
async def echo_message(message):
    await bot.reply_to(message, helper)
