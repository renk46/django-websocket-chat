from django.urls import re_path
from rest_framework import routers

from . import consumers

router = routers.DefaultRouter()

websocket_urlpatterns = [
    re_path(r"api/chat/ws/", consumers.ChatConsumer.as_asgi()),
]
