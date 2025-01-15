from django.shortcuts import render
from django.views import View

# Create your views here.
class Wardrobe(View):
    def get(self, request):
        return render(request, 'wardrobe/wardrobe.html')