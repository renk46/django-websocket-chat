from datetime import datetime
from chat.models import Message
from asgiref.sync import async_to_sync

handlers = []


def ws_request(request=None):
    """Decorator for incoming requests"""

    def inner(func):
        def wrapper(self, data):
            if request == data["request"]:
                return func(self, data["data"]) if "data" in data else func(self)

        handlers.append(wrapper)
        return wrapper

    return inner


class DataService:
    """Service processing ws messages"""

    def __init__(self, _type, consumer):
        self._type = _type
        self.consumer = consumer
        self.groups = []

    def send_to_group(self, room, data):
        """Send format message to group with type INFO"""
        async_to_sync(self.consumer.channel_layer.group_send)(
            room,
            {
                "type": "send_payload_event",
                "payload_type": self._type,
                "payload_data": data,
            },
        )

    def send_response(self, response, data):
        """Send format response to this client"""
        return self.consumer.send_payload(self._type, {"response": response, "data": data})

    def disconnect(self, code=None):
        """Handler for disconnect"""

    def create_message(self, user, channel, message):
        """Create message in storage"""
        return Message.objects.create(
            user=user, channel=channel, message=message, datetime=datetime.now()
        )

    def get_list_messages(self, channel):
        """Get last 30 messages for channel"""
        return [
            {
                "id": message.id,
                "datetime": message.datetime,
                "room": message.channel,
                "text": message.message,
                "author": message.user,
            }
            for message in Message.objects.filter(channel=channel, is_blocked=False).order_by("datetime")[
                :30
            ]
        ]

    def handle_message(self, message):
        """Handler for incoming messages"""
        for handler in handlers:
            handler(self, message)

    @ws_request("WHOAIM")
    def who_i_am(self):
        """Handle event from client 'who i am'"""
        return self.send_response("WHOAIM", {"user": self.consumer.scope["user"]})

    @ws_request("JOIN ROOM")
    def join_room(self, room):
        """Handle event from client 'join room'"""
        async_to_sync(self.consumer.channel_layer.group_add)(
            room, self.consumer.channel_name
        )
        self.send_response("JOIN ROOM", {"result": "success", "room": room})
        self.send_response(
            "MESSAGES LIST ROOM",
            {"room": room, "messages": self.get_list_messages(room)},
        )
        self.groups.append(room)

    @ws_request("LEAVE ROOM")
    def leave_room(self, room):
        """Handle event from client 'leave room'"""
        async_to_sync(self.consumer.channel_layer.group_discard)(
            room, self.consumer.channel_name
        )
        self.send_response("LEAVE ROOM", {"result": "success", "room": room})

    @ws_request("NEW MESSAGE")
    def message(self, data):
        """Handle event from client 'message'"""
        rec = self.create_message(
            self.consumer.scope["user"], data["room"], data["text"]
        )
        self.send_to_group(
            data["room"],
            {
                "response": "NEW MESSAGE",
                "data": {
                    "id": str(rec.id),
                    "datetime": str(rec.datetime),
                    "room": data["room"],
                    "text": data["text"],
                    "author": str(self.consumer.scope["user"]),
                },
            }
        )

    @ws_request("BLOCK MESSAGE")
    def block_message(self, data):
        """Handle event from client 'block_message'"""

        message = Message.objects.get(id=data["id"])
        message.is_blocked = True
        message.save()

        self.send_to_group(
            data["room"],
            {
                "response": "BLOCK MESSAGE",
                "data": {
                    "id": data["id"],
                    "datetime": data["datetime"],
                    "room": data["room"],
                    "author": data["author"],
                },
            },
        )
