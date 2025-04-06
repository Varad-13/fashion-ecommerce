from django.urls import path
from .views import *

urlpatterns = [
    path('', index.as_view(), name='home'),
    path('login/', login.as_view(), name='login'),
    path('logout/', logout.as_view(), name='logout'),
    path('signup/', register.as_view(), name='signup'),
]