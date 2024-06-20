from rest_framework import serializers

from bot.models import MainTableAdmin, LessonFit, TrainerFit


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
