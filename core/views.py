from django.http import HttpResponse
from django.shortcuts import render
from django.views import View

class landing(View):
    def get(self,request):
        return render(request, 'core/landing.html')

class index(View):
    def get(self, request):
        return render(request, 'core/index.html')

class login(View):
    def get(self, request):
        return render(request, 'core/login.html')
    
class register(View):
    def get(self, request):
        return render(request, 'core/register.html')