from django.urls import path
from .views import *

urlpatterns = [
    path('wardrobe', Wardrobe.as_view(), name="wardrobe")
]