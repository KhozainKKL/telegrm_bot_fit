from rest_framework import serializers

from api.models import LessonFit, UserFit, TrainerFit, TelegramUser
from bot.models import UserFitLesson, MainTableAdmin


class LessonFitSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonFit
        fields = "__all__"


class TrainerFitSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainerFit
        fields = "__all__"


class MainTableSerializer(serializers.ModelSerializer):

    lesson = LessonFitSerializer()
    trainer = TrainerFitSerializer()

    class Meta:
        model = MainTableAdmin
        fields = "__all__"


class UserFitSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFit
        fields = "__all__"


class TelegramUserSerializer(serializers.ModelSerializer):
    card = UserFitSerializer()

    class Meta:
        model = TelegramUser
        fields = "__all__"


class UserLessonFitSerializer(serializers.ModelSerializer):
    user = UserFitSerializer()
    lesson = MainTableSerializer()

    class Meta:
        model = UserFitLesson
        fields = "__all__"
