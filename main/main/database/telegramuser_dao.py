import logging
import re

from django.db.utils import OperationalError
from asgiref.sync import sync_to_async
from telebot.types import Chat, User

from bot.models import UserFit, TelegramUser

logger = logging.getLogger(__name__)


@sync_to_async
def get_is_authenticated_tg_user(message: Chat | User):
    try:
        get = TelegramUser.objects.get(telegram_user_id=message.from_user.id)
        print(get)
    except TelegramUser.DoesNotExist:
        return 100


@sync_to_async
def get_phone_in_user_fit(message: Chat | User, data: Chat | User):
    try:
        message = message.text.split(' ')

        def format_phone_number(phone_number):
            phone_number = str(phone_number)
            digits = re.sub(r'\D', '', phone_number)

            formatted_number = '+7-{}-{}-{}-{}'.format(digits[-10:-7], digits[-7:-4], digits[-4:-2], digits[-2:])

            return formatted_number

        phone = UserFit.objects.filter(card=message[0], phone=format_phone_number(message[1]))
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
            set_card = UserFit.objects.get(card=message[0])
            telegram_user, create_status = TelegramUser.objects.update_or_create(
                card=set_card,
                is_authenticated=True,
                telegram_user_id=data.id,
                defaults=defaults_dict)
            with open(f'bot/logging/{data.id}', 'w+', encoding='utf-8') as file:
                if create_status is False:
                    file.write(f'Успешно обновлен user в БД: id:{data.id} Имя:{first_name} Фамилия:{last_name} Никнейм:{username}')
                    logger.info(
                        f'Успешно обновлен user в БД: id:{data.id} Имя:{first_name} Фамилия:{last_name} Никнейм:{username}')
                else:
                    file.write(f'[INFO] = Успешно создан user в БД {first_name} {last_name} {username}')
                    logger.info(f'Успешно создан user в БД {first_name} {last_name} {username}')
                return create_status
    except UserFit.DoesNotExist:
        return 300
