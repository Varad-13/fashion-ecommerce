from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(Category)
admin.site.register(ProductItem)
admin.site.register(FlashSale)
admin.site.register(VirtualModel)
admin.site.register(VirtualPhotos)