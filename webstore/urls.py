from django.urls import path
from .views import *

urlpatterns = [
    path('products/', index.as_view(), name='index'),
    path('target/<str:target>/', target.as_view(), name='target'),
    path('categories/', categories.as_view(), name='categories'),
    path('category/<str:category_slug>/', category.as_view(), name='category'),
    path('products/<int:product_id>/', product.as_view(), name='product'),
    path('tryon/<int:product_id>', tryon_avatar.as_view(), name='tryon'),
    path('tryon/get_tryon/<int:product_id>/<str:model_id>/', check_response.as_view(), name='get_tryon'),
    
    path('tryon/user/<int:product_id>/', UserTryonView.as_view(), name='user_tryon'),
    path('tryon/user/<int:product_id>/poll/', UserTryonPollView.as_view(), name='user_tryon_poll'),
    
    path('search/<str:search_term>/', search.as_view(), name='search'),
    path('api/products/', ProductListView.as_view(), name='product-list'),
]