from django_ws_app.handlers import AbstractHandler, action, send_group
from django_ws_app.response import SuccessResponse

class ChatHandler(AbstractHandler):
    @action
    def new_message(self, data):
        send_group(data["room"], SuccessResponse("NEW MESSAGE", {
            "author": self.get_user(),
            "text": data["text"]
        }))
