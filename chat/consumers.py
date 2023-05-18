import traceback
import json
from jsonschema import validate
from jsonschema.exceptions import ValidationError
from enum import Enum

from channels.generic.websocket import WebsocketConsumer
from chat.service.AuthService import AuthService
from chat.service.DataService import DataService


class MessageTypes(Enum):
    """Message types"""
    AUTH = '0'
    DATA = '1'


schema = {
    "type": "object",
    "properties": {
        "type": {"type": "string"},
    },
    "required": ["type", "payload"],
}

handlers = []


def ws_receive(_type=None):
    """Decorator for receive message"""

    def inner(func):
        def wrapper(self, data):
            if _type == data["type"]:
                return func(self, data["payload"])

        handlers.append(wrapper)
        return wrapper

    return inner


class ChatConsumer(WebsocketConsumer):
    """Chat consumer"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_service = AuthService(MessageTypes.AUTH.value, self)
        self.data_service = DataService(MessageTypes.DATA.value, self)

    def connect(self):
        self.accept()
        self.auth_service.who_are_you()

    def disconnect(self, code):
        self.data_service.disconnect(code)

    def send_payload_event(self, event):
        """Send to client payload event"""
        self.send_payload(event["payload_type"], event["payload_data"])

    def send_payload(self, _type, payload):
        """Send to client payload"""
        self.send(
            text_data=json.dumps({"type": _type, "payload": payload}, default=str)
        )

    def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        try:
            validate(instance=data, schema=schema)
            for handler in handlers:
                handler(self, data)
        except ValidationError:
            self.close()
            print(traceback.print_exc())

    @ws_receive(MessageTypes.AUTH.value)
    def handle_auth(self, data):
        """Handle auth data"""
        self.auth_service.handle_message(data)

    @ws_receive(MessageTypes.DATA.value)
    def handle_data(self, data):
        """Handle data messages"""
        self.data_service.handle_message(data)
