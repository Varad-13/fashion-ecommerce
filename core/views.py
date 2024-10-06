from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.views import View
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError

from .models import *
from django.contrib.auth.models import User

class landing(View):
    def get(self,request):
        return render(request, 'core/landing.html')

class index(View):
    def get(self, request):
        return render(request, 'webstore/index.html')

class login(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('/')
        return render(request, 'core/login.html')
    def post(self, request):
        user_email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=user_email)
        except:
            messages.error(request, "User with this email does not exist.")
            return redirect('/login/')

        auth = authenticate(username=user.username, password=password)
        if auth == None:
            messages.error(request, "Please check your password.")
            return redirect('/login/')

        if auth is None:
            return redirect('/login/')
        
        else:
            auth_login(request, user)
            return redirect('/')
    
class logout(View):
    def get(self, request):
        if request.user.is_authenticated:
            auth_logout(request)
            return redirect('/login/')

class register(View):
    def get(self, request):
        return render(request, 'core/register.html')
    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if User.objects.filter(email = email).exists():
            messages.error(request, "User with this email already exists!")
            return redirect('/signup')
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('/signup')

        try:
            password_validation.validate_password(password=password)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect('/signup')


        new_user = User.objects.create(
            username = email,
            first_name = name,
            email = email,
            password = make_password(password)
        )
        userprofile = Userprofile.objects.create(
            name = name,
            user = new_user,
            email = email,
        )

        auth_login(request, new_user)
        return redirect('/')