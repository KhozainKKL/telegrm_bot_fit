import telebot
import aiofiles
from asgiref.sync import sync_to_async
from django.conf import settings

from bot.models import MONTHS_RU
from main.database.config import MainConfigTelegramBot, AddNewUserMiddleware as middleware, \
    AllMarkUpForButtonBot as markup, SampleTextBot as smpl_text
from telebot.async_telebot import AsyncTeleBot

bot = AsyncTeleBot(settings.TG_API_KEY, parse_mode='HTML')
telebot.logger.setLevel(settings.LOGLEVEL)

bot.setup_middleware(middleware(bot))
config = MainConfigTelegramBot(bot)


@bot.message_handler(regexp='Записаться на групповое занятие 🤸‍♂️')
@config.require_authentication
async def send_calendar(message):
    await bot.send_message(message.chat.id, "Как вы хотите записаться на групповое занятие?",
                           reply_markup=markup.get_main_lesson_all())

    @bot.callback_query_handler(func=lambda call: call.data in ['by_type', 'by_trainer', 'any'])
    async def choose_option(call):
        result = await config.get_data_lesson(call.data)
        if call.data == "by_type":
            await choose_by_type(call.message, result)
        elif call.data == "by_trainer":
            await choose_by_trainer(call.message, result)
        elif call.data == "any":
            await choose_any(call.message, result)

    async def choose_by_type(message, lesson_types):
        await bot.edit_message_text("Выберите вид занятия:", message.chat.id, message.message_id,
                                    reply_markup=markup.get_main_lesson_choose_by_type(lesson_types))

    @bot.callback_query_handler(func=lambda call: call.data.startswith('type_'))
    async def handle_lesson_type(call):
        lesson_type = call.data.split('_')[1]
        lesson_check = []
        dates = await config.get_data_lesson(call.data, data=lesson_type)
        for lesson in dates['lesson']:
            if (lesson.max_number_of_recorded - lesson.number_of_recorded) <= 3:
                lesson_check.append(config.formatted_date(lesson))

        if lesson_check:
            await bot.edit_message_text(
                f"<blockquote>️<i> Обратите внимание, что на занятие(я): \n<b>{', '.join(lesson_check)}\n"
                f"осталось мало мест.</b> </i></blockquote>\nВыберите дату занятия:",
                call.message.chat.id, call.message.message_id,
                reply_markup=markup.get_main_lesson_handle_lesson_type(dates['date']))
        elif not lesson_check:
            await bot.edit_message_text(f"Выберите дату занятия:", call.message.chat.id, call.message.message_id,
                                        reply_markup=markup.get_main_lesson_handle_lesson_type(dates['date']))

    async def choose_by_trainer(message, trainers):
        await bot.edit_message_text("Выберите тренера:", message.chat.id, message.message_id,
                                    reply_markup=markup.get_main_lesson_choose_by_trainer(trainers))

    @bot.callback_query_handler(func=lambda call: call.data.startswith('trainer_'))
    async def handle_trainer_lesson_type(call):
        trainer = call.data.split('_')[1]
        print(trainer)
        lesson = await config.get_data_lesson(call.data, data=trainer)
        await bot.edit_message_text(chat_id=call.message.chat.id, text="Выберите вид занятия:",
                                    message_id=call.message.message_id,
                                    reply_markup=markup.get_main_lesson_handle_trainer_lesson_type(lesson, trainer))

    @bot.callback_query_handler(func=lambda call: call.data.startswith('trainers_lesson_'))
    async def handle_trainer_lesson_date(call):
        lesson = call.data.split('_')[2]
        trainer_id = call.data.split('_')[3]
        data = {'lesson': lesson, 'trainer_id': trainer_id}
        lesson_check = []
        data = await config.get_data_lesson(call.data, data=data)

        for lesson in data['lesson']:
            if (lesson.max_number_of_recorded - lesson.number_of_recorded) <= 3:
                lesson_check.append(config.formatted_date(lesson))
        if lesson_check:
            await bot.edit_message_text(
                f"<blockquote>️<i> Обратите внимание, что на занятие(я): \n<b>{', '.join(lesson_check)}\n"
                f"осталось мало мест.</b> </i></blockquote>\nВыберите дату занятия:",
                call.message.chat.id, call.message.message_id,
                reply_markup=markup.get_main_lesson_handle_lesson_type(data['date']))
        elif not lesson_check:
            await bot.edit_message_text(f"Выберите дату занятия:", call.message.chat.id, call.message.message_id,
                                        reply_markup=markup.get_main_lesson_handle_lesson_type(data['date']))

    async def choose_any(message, dates):
        lesson_check = []
        for lesson in dates['lesson']:
            if (lesson.max_number_of_recorded - lesson.number_of_recorded) <= 3:
                lesson_check.append(config.formatted_date(lesson))
        if lesson_check:
            await bot.edit_message_text(
                f"<blockquote>️<i> Обратите внимание, что на занятие(я): \n<b>{', '.join(lesson_check)}\n"
                f"осталось мало мест.</b> </i></blockquote>\nВыберите дату занятия:",
                message.chat.id, message.message_id,
                reply_markup=markup.get_main_lesson_handle_lesson_type(dates['date']))
        elif not lesson_check:
            await bot.edit_message_text(f"Выберите дату занятия:", message.chat.id, message.message_id,
                                        reply_markup=markup.get_main_lesson_handle_lesson_type(dates['date']))

    @bot.callback_query_handler(func=lambda call: call.data.startswith('date_'))
    async def handle_date(call):
        date = call.data.split('_')[1]
        try:
            date_relative = call.data.split('_')[2]
        except Exception:
            date_relative = None

        data = await config.get_data_lesson(call.data, data=date, message=call.message.chat.id,
                                            relative_user=date_relative)
        if not data['state'] and data['relative_user']:
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        text=smpl_text.user_true_relative_yes(),
                                        message_id=call.message.message_id,
                                        reply_markup=markup.get_main_lesson_handle_date_relative_user(data, date))
        elif not data['state'] and not data['relative_user']:

            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        text=smpl_text.user_true_relative_none(),
                                        message_id=call.message.message_id, reply_markup=markup.back_to_month())
        if data['state'] and not date_relative and (
                data['tmp'][0].number_of_recorded < data['tmp'][0].max_number_of_recorded):
            await config.set_data_user_lesson(call, date, relative_user=date_relative)
            if not data['tmp'][0].check_canceled:
                if data['tmp'][0].number_of_recorded < data['tmp'][0].max_number_of_recorded:
                    formatted_date = config.formatted_date(data['tmp'][0])
                    await bot.edit_message_text(chat_id=call.message.chat.id,
                                                text=f"<b>Вы записаны к тренеру: {data['tmp'][0].trainer}\n"
                                                     f"На занятие: {data['tmp'][0].lesson}\n"
                                                     f" {formatted_date}</b>", message_id=call.message.message_id)
                    await bot.send_sticker(call.message.chat.id,
                                           sticker=smpl_text.sticker_true_lesson())
        elif data['state'] and date_relative and data['state_relative_user'] and (
                data['tmp'][0].number_of_recorded < data['tmp'][0].max_number_of_recorded):
            await config.set_data_user_lesson(call, date, relative_user=date_relative)
            formatted_date = config.formatted_date(data['tmp'][0])
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        text=f"<b>Родственник {data['relative_user'].first_name} "
                                             f"{data['relative_user'].last_name}\n записан(а) к тренеру: "
                                             f"{data['tmp'][0].trainer}\n"
                                             f"На занятие: {data['tmp'][0].lesson}\n"
                                             f" {formatted_date}</b>", message_id=call.message.message_id)
            await bot.send_sticker(call.message.chat.id,
                                   sticker=smpl_text.sticker_true_lesson())
        elif data['state'] and date_relative and not data['state_relative_user']:
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        text=smpl_text.user_true_relative_true(),
                                        message_id=call.message.message_id, reply_markup=markup.back_to_month())
        elif data['state'] and not date_relative and (
                data['tmp'][0].number_of_recorded >= data['tmp'][0].max_number_of_recorded):
            await config.set_data_user_lesson(call, date, relative_user=date_relative, is_reserve=True)
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        text=smpl_text.user_is_reserve(),
                                        message_id=call.message.message_id, reply_markup=markup.back_to_month())
        elif data['state'] and date_relative and data['state_relative_user'] and (
                data['tmp'][0].number_of_recorded >= data['tmp'][0].max_number_of_recorded):

            await config.set_data_user_lesson(call, date, relative_user=date_relative, is_reserve=True)
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        text=smpl_text.relative_user_is_reserve(),
                                        message_id=call.message.message_id, reply_markup=markup.back_to_month())

    @bot.callback_query_handler(func=lambda call: call.data == "back_to_month")
    async def back_to_month(call):
        await bot.edit_message_text(chat_id=call.message.chat.id, text="Как вы хотите записаться на групповое занятие?",
                                    message_id=call.message.message_id, reply_markup=markup.get_main_lesson_all())


@bot.message_handler(regexp='Расписание и описание групповых занятий 🧘‍♂️')
@config.require_authentication
async def schedule(message):
    sent_message = await bot.send_message(message.chat.id, "Загружаем расписание занятий.")
    file_path = await config.get_data_lesson(message)
    if not file_path:
        await bot.delete_message(message.chat.id, sent_message.message_id)
        await bot.send_message(message.chat.id, "Расписания еще нет.")

    if file_path:
        for week in file_path:
            async with aiofiles.open(week[0].schedule.path, 'rb') as file:
                await bot.send_document(message.chat.id, file)
        await bot.delete_message(message.chat.id, sent_message.message_id)

        await bot.send_message(message.chat.id, "Подробное описание тренировок.",
                               reply_markup=markup.button_get_schedule_lesson_group())

    @bot.callback_query_handler(func=lambda call: call.data == 'schedule_')
    async def choose_schedule(call):
        result = await config.get_data_lesson(call.data)
        await bot.edit_message_text("Выберите вид занятия:", call.message.chat.id, call.message.message_id,
                                    reply_markup=markup.button_get_schedule_lesson_group(result))

        @bot.callback_query_handler(func=lambda call: call.data == "back_to_lesson")
        async def back_to_lesson(call):
            await bot.edit_message_text(chat_id=call.message.chat.id,
                                        text="Подробное описание тренировок.",
                                        message_id=call.message.message_id,
                                        reply_markup=markup.button_get_schedule_lesson_group(result))

    @bot.callback_query_handler(func=lambda call: call.data.startswith('schedule_type_'))
    async def choose_schedule(call):
        lesson_type = call.data.split('_')[2]
        result = await config.get_data_lesson(call.data, data=lesson_type)
        await bot.edit_message_text(chat_id=call.message.chat.id,
                                    text=f'<b>Название: {result.title}</b>\n'
                                         f'Описание: {result.description}',
                                    message_id=call.message.message_id, reply_markup=markup.button_back_to_lesson())


@bot.message_handler(regexp='Занятия на которые Вы записаны📆')
@config.require_authentication
async def my_lesson(message):
    global show, show_relative
    data = await config.get_data_my_lesson(message)
    if not data['user']:
        await bot.send_message(message.chat.id, "Вы пока не записаны на занятия.")
    elif data['user']:
        show = markup.button_for_lesson_you_zapis(data['user'], data['user_id'])
        await bot.send_message(message.chat.id, "Список ваших занятий:",
                               reply_markup=show)
    if data['relative_user']:
        show_relative = markup.button_for_lesson_you_zapis_relative(data['relative_user'], data['user_id'])
        await bot.send_message(message.chat.id, "Список занятий Вашего родственника:",
                               reply_markup=show_relative)

    @bot.callback_query_handler(lambda query: query.data.startswith('lesson_'))
    async def lesson_info(query):
        lesson_id = int(query.data.split('_')[1])
        user_id = query.data.split('_')[2]
        key = query.data.split('_')[3]
        user_lesson = await config.get_data_my_lesson(query.data, data=lesson_id)
        formatted_date = config.formatted_date(user_lesson['lesson'][0])
        if not user_lesson['user']:
            lesson_info_text = (
                f"<b>Занятие:</b> {user_lesson['lesson'][0].lesson}\n"
                f"<b>Дата и время:</b> {formatted_date}\n"
                f"<b>Тренер:</b> {user_lesson['lesson'][0].trainer.first_name} {user_lesson['lesson'][0].trainer.last_name}\n"
            )
        elif user_lesson['user']:
            lesson_info_text = (
                f"<blockquote>️<i><b>Обращаем Ваше внимание: что Вы находитесь в резерве.</b></i></blockquote>️"
                f"<b>Занятие:</b> {user_lesson['lesson'][0].lesson}\n"
                f"<b>Дата и время:</b> {formatted_date}\n"
                f"<b>Тренер:</b> {user_lesson['lesson'][0].trainer.first_name} {user_lesson['lesson'][0].trainer.last_name}\n"
            )
        await bot.edit_message_text(chat_id=query.message.chat.id, text=lesson_info_text,
                                    message_id=query.message.message_id,
                                    reply_markup=markup.button_for_lesson_you_zapis_unsubscribe(
                                        lesson_id, user_id, key))

    @bot.callback_query_handler(lambda query: query.data == 'back_to_lessons_user')
    async def back_to_lessons(query):

        await bot.edit_message_text(chat_id=query.message.chat.id, text="Список ваших занятий:",
                                    message_id=query.message.message_id,
                                    reply_markup=show)

    @bot.callback_query_handler(lambda query: query.data == 'back_to_lessons_relative_user')
    async def back_to_lessons(query):
        await bot.edit_message_text(chat_id=query.message.chat.id, text="Список занятий Вашего родственника:",
                                    message_id=query.message.message_id,
                                    reply_markup=show_relative)

    @bot.callback_query_handler(lambda query: query.data.startswith('unsubscribe_'))
    async def unsubscribe_from_lesson(query):
        lesson_id = int(query.data.split('_')[1])
        user_id = query.data.split('_')[2]

        await config.get_data_my_lesson(query.data, data=lesson_id, user_id=user_id)
        await bot.edit_message_text(chat_id=query.message.chat.id, text="Вы успешно отписались от занятия.",
                                    message_id=query.message.message_id)


async def canceled_lesson_post_message_users(data):
    message_help = smpl_text.canceled_lesson_post_message_users(data)
    for user in data['tg_users']:
        await bot.send_message(chat_id=user, text=message_help)


async def change_lesson_post_message_users(data):
    message_help = smpl_text.change_lesson_post_message_users(data)
    for user in data['tg_users']:
        await bot.send_message(chat_id=user, text=message_help)


async def get_for_user_is_not_reserve(data):
    message_help = smpl_text.get_for_user_is_not_reserve(data)
    for user in data['tg_users']:
        await bot.send_message(chat_id=user, text=message_help)


async def send_promo_users(result):
    message_help = smpl_text.send_promo_users(result)
    for user in result['users']:
        await bot.send_photo(chat_id=user, photo=open(result["instance"]["image"], "rb"), caption=message_help)


@bot.message_handler(func=lambda message: True)
@config.require_authentication
async def echo_message(message):
    await bot.send_message(message.chat.id, smpl_text.main_text(), reply_markup=markup.reply_keyboard_button_main())
