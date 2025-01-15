from django.db import models
from core.models import Userprofile

class WardrobeItem(models.Model):
    image = models.ImageField(upload_to='wardrobe/')

class UserImage(models.Model):
    user = models.ForeignKey(Userprofile, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='user/')

class TryOn(models.Model):
    image = models.ImageField(upload_to='tryon/')
    user_image = models.ForeignKey(UserImage, on_delete=models.CASCADE)
    wardrobe_image = models.ForeignKey(WardrobeItem, on_delete=models.CASCADE)