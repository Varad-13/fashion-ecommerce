from django.db import models
from core.models import Userprofile

class Category(models.Model):
    name = models.TextField()
    thumbnail = models.ImageField(upload_to='category/')

class ProductItem(models.Model):
    product_image = models.ImageField(upload_to='product/')
    product_name = models.TextField()
    price = models.IntegerField()

class VirtualModel(models.Model):
    model_photo = models.ImageField(upload_to='model/')
    model_name = models.TextField()

class VirtualPhotos(models.Model):
    photo = models.ImageField(upload_to='generated-photos/')
    model = models.ForeignKey(VirtualModel, on_delete=models.CASCADE)
    product = models.ForeignKey(ProductItem, on_delete=models.CASCADE, related_name='virtual_photos')

class UserPhotos(models.Model):
    photo = models.ImageField(upload_to='user-photos/')
    user = models.ForeignKey(Userprofile, on_delete=models.CASCADE, related_name='user_tryon')
    product = models.ForeignKey(ProductItem, on_delete=models.CASCADE, related_name='user_photos')
