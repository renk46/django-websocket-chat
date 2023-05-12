from asgiref.sync import async_to_sync
from rest_framework_simplejwt.authentication import JWTAuthentication
from channels.auth import login

class AuthService():
    def __init__(self, consumer):
        self.consumer = consumer
    
    def send_response(self, message):
        self.consumer.send_payload("AUTH", message)
    
    def processing(self, message):
        jwt = JWTAuthentication()
        try:
            token = jwt.get_validated_token(message)
            user = jwt.get_user(token)
            async_to_sync(login)(self.consumer.scope, user)
            self.send_response("SUCCESS")
        except Exception as e:
            self.send_response("TOKENEXPIRED")
            self.consumer.close()
            print("Exception %s" % str(e))

    def who_are_you(self):
        self.send_response("WHOAREYOU")