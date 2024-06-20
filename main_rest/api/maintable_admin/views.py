from rest_framework import viewsets
from .serializer import MainTableSerializer
from bot.models import MainTableAdmin


class MainTableViewSet(viewsets.ModelViewSet):
    queryset = MainTableAdmin.objects.all()
    serializer_class = MainTableSerializer
