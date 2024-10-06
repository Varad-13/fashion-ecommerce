from django.urls import path
from .views import *

urlpatterns = [
    path('', index.as_view(), name='index'),
    path('target/<str:target>/', target.as_view(), name='target'),
    path('categories/', categories.as_view(), name='categories'),
    path('category/<str:category_slug>/', category.as_view(), name='category'),
    path('products/<int:product_id>/', product.as_view(), name='product'),
]