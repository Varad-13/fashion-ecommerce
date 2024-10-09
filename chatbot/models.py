from django.db import models
from core.models import Userprofile
from .parse_markdown import parse_markdown
# Create your models here.

class Chat(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(Userprofile, on_delete=models.CASCADE, related_name='chats')
    created = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.title

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=7)
    content = models.TextField()
    content_html = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['timestamp']