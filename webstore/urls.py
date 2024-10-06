from django.urls import path
from .views import *

urlpatterns = [
    path('', index.as_view(), name='index'),
    path('categories/', categories.as_view(), name='categories'),
    path('products/<int:product_id>', product.as_view(), name='product'),
]