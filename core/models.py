from django.db import models
from django.contrib.auth.models import User

class UserImages(models.Models):
    file = models.ImageField(upload_to="/user-images")

class Userprofile(models.Model):
    name = models.TextField()
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    images = models.ManyToManyField(UserImages, related_name="user")
    