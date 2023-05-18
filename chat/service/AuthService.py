import traceback
from asgiref.sync import async_to_sync
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.authentication import InvalidToken, TokenError
from channels.auth import login


class AuthService:
    """Authentication service from WebSocket connection"""

    def __init__(self, _type, consumer):
        self._type = _type
        self.consumer = consumer

    def send_response(self, message):
        """Send format response to this client"""
        self.consumer.send_payload(self._type, message)

    def handle_error(self):
        """Send error response to client"""
        self.send_response("TOKENEXPIRED")
        self.consumer.close()
        print(traceback.print_exc())

    def handle_message(self, message):
        """Handler for incoming messages"""
        jwt = JWTAuthentication()
        try:
            token = jwt.get_validated_token(message)
            user = jwt.get_user(token)
            async_to_sync(login)(self.consumer.scope, user)
            self.send_response("SUCCESS")
        except InvalidToken:
            self.handle_error()
        except TokenError:
            self.handle_error()

    def who_are_you(self):
        """Check session authentication"""
        if self.consumer.scope["user"].is_authenticated:
            self.send_response("SUCCESS")
        else:
            self.send_response("WHOAREYOU")
