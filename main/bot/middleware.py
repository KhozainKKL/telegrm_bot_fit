import logging
from telebot import BaseMiddleware
from main.database.telegramuser_dao import get_is_authenticated_tg_user, get_phone_in_user_fit

logger = logging.getLogger(__name__)


class AddNewUserMiddleware(BaseMiddleware):
    def __init__(self, bot):
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

        if await get_is_authenticated_tg_user(message) == 100:
            await self.bot.send_message(message.chat.id,
                                        "Вы не авторизованы. Пожалуйста, введите номер Вашей карты клиента \n"
                                        "и номер телефона указанные в договоре \n(Например: 111 88005551011):")
            if await get_phone_in_user_fit(message, my_data) == 301:
                await self.bot.send_message(message.chat.id,
                                            "<b>Успех: Приятного пользования.</b>")

    async def post_process(self, message, data, exception):
        pass
