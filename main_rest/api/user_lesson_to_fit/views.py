from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializer import UserLessonFitSerializer, TelegramUserSerializer
from bot.models import UserFitLesson
from ..models import TelegramUser


class UserLessonFitViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer

    @action(detail=True, methods=["get"])
    def get_for_telegram(self, request, pk=None):
        profile = TelegramUser.objects.get(telegram_user_id=pk)
        lessons = UserFitLesson.objects.filter(user=profile.card)
        serializer = UserLessonFitSerializer(lessons, many=True)
        return Response(serializer.data)
