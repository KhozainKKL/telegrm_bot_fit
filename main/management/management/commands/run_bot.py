import logging

from django.conf import settings
from django.core.management.base import BaseCommand
import asyncio

from bot.main_bot import bot

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Запускаем бота'

    def handle(self, *args, **options):
        try:
            asyncio.run(bot.infinity_polling(logger_level=settings.LOGLEVEL))
        except Exception as err:
            logger.error(f'Ошибка: {err}')
