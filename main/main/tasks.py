from asgiref.sync import async_to_sync

from bot.main_bot import send_promo_users
from main.celery import app


# @app.task
# def send_hall_promo(instance):
#     async_to_sync(send_promo_users)(instance)
