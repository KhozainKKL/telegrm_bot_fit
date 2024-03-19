import logging
from asgiref.sync import sync_to_async
from telebot import BaseMiddleware
from bot.models import TelegramUser, UserFit

logger = logging.getLogger(__name__)


class AddNewUserMiddleware(BaseMiddleware):
    def __init__(self):
        super(AddNewUserMiddleware, self).__init__()
        self.card_id_requests = {}
        self.update_types = ['message']

    async def pre_process(self, message, data):
        pass

    async def post_process(self, message, data, exception):
        pass



# try:
#     check_user = await sync_to_async(TelegramUser.objects.get)(telegram_user_id=message.from_user.id)
#     print(check_user)
# except TelegramUser.DoesNotExist:
#     await bot.send_message(message.chat.id,
#                            "Вы авторизованы. Пожалуйста, введите номер Вашей карты клиента:")
#
#     async def check_card(message):
#         try:
#             check_card = await sync_to_async(UserFit.objects.get)(card=message.text)
#             print(check_card)
#             await bot.send_message(message.chat.id,
#                                    check_card)
#         except UserFit.DoesNotExist:
#             await bot.send_message(message.chat.id,
#                                    "Вы являетесь нашим клиентом.")
#
#     await bot.register_message_handler(callback=check_card)
