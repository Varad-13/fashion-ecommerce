from django.urls import path
from .views import *

urlpatterns = [
    path('', Wardrobe.as_view(), name="wardrobe")
]