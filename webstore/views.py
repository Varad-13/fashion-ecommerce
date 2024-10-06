from django.shortcuts import render, get_object_or_404
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

class category(View):
    def get(self, request, category_slug):
        category = get_object_or_404(Category, slug=category_slug)
        context = {}
        context["category"] = category

        return render(request, 'webstore/category.html', context)

class target(View):
    def get(self, request, target):
        targets = ["Men", "Women", "Unisex", "Children"]
        context = {}
        for t in targets:
            if t.lower() == target.lower():
                products = ProductItem.objects.filter(target=t)
                context["target"] = t
                context["products"] = products
        return render(request, 'webstore/target.html', context)

class product(View):
    def get(self, request, product_id):
        product = ProductItem.objects.get(id=product_id)
        avatars = VirtualModel.objects.all()
        context = {}
        context['product'] = product
        context['avatars'] = avatars
        return render(request, 'webstore/product_page.html', context)
    

class tryon_avatar(View):
    def get(self, request, product_id):
        product = ProductItem.objects.get(id=product_id)
        avatars = VirtualModel.objects.all()
        context = {}
        context['product'] = product
        context['avatars'] = avatars
        return render(request, 'webstore/virtual_try_on.html', context)
    
    def post(self, request):
        product_id = request.POST.get('product')
        model_id = request.POST.get('avatar')
        model = VirtualModel.objects.get(model_name=model_id)
        product = ProductItem.objects.get(id=product_id)
        if VirtualPhotos.objects.filter(model=model, product=product).exists():
            image = VirtualPhotos.objects.get(model=model, product=product)
            return image.url
        else:
            pass

class get_image(View):
    def get(self, request, product_id, model_id):
        model = VirtualModel.objects.get(model_name=model_id)
        product = ProductItem.objects.get(id=product_id)
        if VirtualPhotos.objects.filter(model=model, product=product).exists():
            image = VirtualPhotos.objects.get(model=model, product=product)
            return render(request, 'partials/image', image) 
        else:
            return render(request, 'partials/loading')