from asgiref.sync import async_to_sync

class InfoService():
    def __init__(self, consumer):
        self.consumer = consumer
        self.groups = []

    def send_to_group_message(self, room, data):
        async_to_sync(self.consumer.channel_layer.group_send)(room, {
            "type": "send_payload_event",
            "payload_type": "MESSAGE",
            "payload_data": data
        })

    def disconnect(self, close_code):
        for room in self.groups:
            self.send_to_group_message(room, {
                "room": room,
                "text": "{0} disconnect from room".format(str(self.consumer.scope["user"])),
                "author": "SYSTEM"
            })
            
    def send_response(self, message):
        self.consumer.send_payload("INFO", message)

    def processing(self, message):  
        if message["request"] == "WHOAIM":
            self.send_response({
                "response": str(self.consumer.scope["user"])
            })

        elif message["request"] == "JOIN ROOM":
            room = message["data"]
            async_to_sync(self.consumer.channel_layer.group_add)(room, self.consumer.channel_name)
            self.send_to_group_message(room, {
                "room": room,
                "text": "{0} joined to room".format(str(self.consumer.scope["user"])),
                "author": "SYSTEM"
            })
            self.send_response({
                "response": "JOINED TO %s" % room
            })
            self.groups.append(room)
        
        elif message["request"] == "MESSAGE":
            self.send_to_group_message(message["room"], {
                "room": message["room"],
                "text": message["text"],
                "author": str(self.consumer.scope["user"])
            })