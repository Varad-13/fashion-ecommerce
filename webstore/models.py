from django.db import models
from core.models import Userprofile

class Category(models.Model):
    name = models.TextField()
    slug = models.TextField(unique=True, null=True, blank=True)
    thumbnail = models.ImageField(upload_to='category/')
    def __str__(self):
        return(self.name)

class ProductItem(models.Model):
    product_image = models.ImageField(upload_to='product/')
    product_name = models.TextField()
    target = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.IntegerField()
    def __str__(self):
        return(self.product_name)
    class Meta:
        ordering = ["-id"]

class FlashSale(models.Model):
    product = models.OneToOneField(ProductItem, on_delete=models.CASCADE, related_name='sale')
    price = models.IntegerField()
    class Meta:
        ordering = ["-id"]

class VirtualModel(models.Model):
    model_photo = models.ImageField(upload_to='model/')
    model_name = models.TextField()
    def __str__(self):
        return(self.model_name)

class VirtualPhotos(models.Model):
    photo = models.ImageField(upload_to='generated-photos/')
    model = models.ForeignKey(VirtualModel, on_delete=models.CASCADE, related_name='photo')
    product = models.ForeignKey(ProductItem, on_delete=models.CASCADE, related_name='virtual_photos')
    def __str__(self):
        model = self.model.model_name
        product = self.product.product_name
        return product + model

class UserPhotos(models.Model):
    photo = models.ImageField(upload_to='user-photos/')
    user = models.ForeignKey(Userprofile, on_delete=models.CASCADE, related_name='user_tryon')
    product = models.ForeignKey(ProductItem, on_delete=models.CASCADE, related_name='user_photos')

class Wardrobe(models.Model):
    photo = models.ImageField(upload_to='wardrobe/')
    user = models.ForeignKey(Userprofile, on_delete=models.CASCADE, related_name='wardrobe_items')
