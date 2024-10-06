from django.urls import path
from .views import *

urlpatterns = [
    path('', index.as_view(), name='index'),
    path('/login', index.as_view(), name='login'),
    path('/signup', index.as_view(), name='signup'),
]