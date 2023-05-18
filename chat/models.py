import uuid
from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    channel = models.CharField(max_length=255)
    message = models.TextField()
    datetime = models.DateTimeField()
    is_blocked = models.BooleanField(default=False)
