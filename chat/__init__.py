from django_ws_app.handlers import Handlers
from chat.handler import ChatHandler

Handlers().register(ChatHandler)