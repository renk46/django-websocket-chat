import json
from jsonschema import validate

from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from chat.service.AuthService import AuthService
from chat.service.InfoService import InfoService

schema = {
    "type": "object",
    "properties": {
        "t": {"type": "string"},
    },
    "required": ["t", "p"],
}

class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_service = AuthService(self)
        self.info_service = InfoService(self)

    def connect(self):
        self.accept()
        self.auth_service.who_are_you()

    def disconnect(self, close_code):
        self.info_service.disconnect(close_code)

    def processing_message(self, message):
        type = message["t"]
        data = message["p"]
        if type == "AUTH":
            self.auth_service.processing(data)
        elif type == "INFO":
            self.info_service.processing(data)

    def send_payload_event(self, event):
        self.send_payload(event["payload_type"], event["payload_data"])

    def send_payload(self, type, payload):
        self.send(text_data=json.dumps({"t": type, "p": payload}))

    def receive(self, text_data):
        data = json.loads(text_data)
        try:
            validate(instance=data, schema=schema)
            self.processing_message(data)
        except Exception as e:
            self.close()
            print(str(e))
