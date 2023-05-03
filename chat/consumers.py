import json
from jsonschema import validate
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from channels.auth import login

schema = {
    "type": "object",
    "properties": {
        "type": {"type": "string"},
        "message": {"type": "string"},
    },
    "required": ["type", "message"],
}

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        self.send_json("AUTH", "WHOAREYOU")

    def disconnect(self, close_code):
        pass

    def auth(self, message):
        def send_response(message):
            self.send_json("AUTH", message)

        jwt = JWTAuthentication()
        try:
            token = jwt.get_validated_token(message)
            user = jwt.get_user(token)
            async_to_sync(login)(self.scope, user)
            send_response("SUCCESS")
        except Exception as e:
            send_response("TOKENEXPIRED")
            self.close()
            print("Exception %s" % str(e))

    def info(self, message):
        def send_response(message):
            self.send_json("INFO", message)

        parts = message.split()

        if parts[0] == "WHOAIM":
            send_response(str(self.scope["user"]))
        if len(parts) >= 3:
            if parts[0] == "JOIN" and parts[1] == "ROOM":
                room = parts[2]
                async_to_sync(self.channel_layer.group_add)(room, self.channel_name)
                send_response("JOINED TO %s" % room)

    def message(self, message):
        def send_response(message):
            self.send_json("MESSAGE", message)

        parts = message.split(' ', 1)
        if len(parts) == 2:
            async_to_sync(self.channel_layer.group_send)(
                parts[0],
                {
                    "type": "chat_message",
                    "room": parts[0],
                    "text": parts[1],
                    "author": str(self.scope["user"])
                }
            )

    def processing_message(self, message):
        type = message["type"]
        data = message["message"]
        if type == "AUTH":
            self.auth(data)
        elif type == "INFO":
            self.info(data)
        elif type == "MESSAGE":
            self.message(data)

    def chat_message(self, event):
        self.send_json("MESSAGE", {
            "room": event["room"],
            "text": event["text"],
            "author": event["author"],
        })

    def send_json(self, type, message):
        self.send(text_data=json.dumps({"type": type, "message": message}))

    def receive(self, text_data):
        message = json.loads(text_data)
        try:
            validate(instance=message, schema=schema)
            self.processing_message(message)
        except Exception as e:
            self.close()
            print(str(e))
