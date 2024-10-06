from django.shortcuts import render
from django.views import View
from .models import *

# Create your views here.
class index(View):
    def get(self, request):
        categories = Category.objects.all()
        targets = ["Men", "Women", "Unisex", "Children"]
        sale = FlashSale.objects.all()
        products = {target: ProductItem.objects.filter(target=target) 
                    for target in targets
                    if ProductItem.objects.filter(target=target).exists()
                    }

        context = {
            'categories': categories,
            'sales': sale,
            'products': products,
        }
        
        return render(request, 'webstore/index.html', context)

class categories(View):
    def get(self, request):
        categories = Category.objects.all()
        
        return render(request, 'webstore/categories.html', {'categories':categories})
    
class product(View):
    def get(self, request, product_id):
        product = ProductItem.objects.get(id=product_id)
        avatars = VirtualModel.objects.all()
        context = {}
        context['product'] = product
        context['avatars'] = avatars
        return render(request, 'webstore/product_page.html', context)