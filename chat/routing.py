from django.urls import re_path, path, include
from rest_framework import routers

from . import consumers
from . import views

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)

websocket_urlpatterns = [
    re_path(r"api/chat/ws/", consumers.ChatConsumer.as_asgi()),
]

urlpatterns = [
    path('', include(router.urls)),
]