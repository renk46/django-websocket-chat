import json
from jsonschema import validate

from channels.generic.websocket import WebsocketConsumer

schema = {
    "type": "object",
    "properties": {
        "type": {"type": "string"},
        "message": {"type": "string"},
    },
}

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        print("{0} - CONNECTED".format(self.scope["user"]))
        self.accept()
        self.send(text_data=json.dumps("AUTH"))

    def disconnect(self, close_code):
        pass

    def processing_message(self, message):
        print(message)

    def receive(self, text_data):
        message = json.loads(text_data)
        if validate(instance=message, schema=schema) == None:
            self.processing_message(message)
        print(validate(instance=message, schema=schema))

        # message = text_data_json["message"]
        # self.send(text_data=json.dumps({"message": message}))