from datetime import datetime

from asgiref.sync import async_to_sync
from django.conf import settings

from bot.main_bot import send_promo_users
from bot.models import TelegramUser
from main.celery import app
from main_table_admin.models import HallPromo


@app.task
def publish_object(request, object_id):
    image = (
        HallPromo.objects.filter(id=object_id).values_list("image", flat=True).first()
    )
    result = {"users": {}, "instance": {}}
    for user in TelegramUser.objects.all().values_list("telegram_user_id", flat=True):
        result["users"][f"{user}"] = user
    result["instance"] = {
        "title": request["title"],
        "description": request["description"],
        "date_at": datetime.strptime(request["date_at"], "%d.%m.%Y"),
        "date_to": datetime.strptime(request["date_to"], "%d.%m.%Y"),
        "promo": request["promo"],
        "image": f"{settings.BASE_DIR}/media/{image}",
    }
    async_to_sync(send_promo_users)(result)
