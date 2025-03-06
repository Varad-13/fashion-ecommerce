import json
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from .models import *
from gradio_client import Client, handle_file
import threading
from FashionEcommerce.settings import BASE_DIR

outfit_anyone = Client("HumanAIGC/OutfitAnyone")
IDM_VTON = Client("yisol/IDM-VTON")

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
    
class search(View):
    def get(self, request, search_term):
        products = ProductItem.objects.filter(product_name__contains = search_term)
        context = {}
        context['products'] = products
        return render(request, 'webstore/search.html', context)

class ProductListView(View):
    def get(self, request):
        products = ProductItem.objects.all().values('product_name', 'target', 'category', 'price')  # Adjust fields as needed
        return JsonResponse(list(products), safe=False)

class tryon_avatar(View):
    def get(self, request, product_id):
        product = ProductItem.objects.get(id=product_id)
        avatars = VirtualModel.objects.all()
        context = {}
        context['product'] = product
        context['avatars'] = avatars
        return render(request, 'webstore/virtual_try_on.html', context)
    
    def post(self, request, product_id):
        data = json.loads(request.body)
        product_id = data.get('product')
        model_id = data.get('avatar')
        print(product_id, model_id)
        model = VirtualModel.objects.get(id=model_id)
        product = ProductItem.objects.get(id=product_id)
        if VirtualPhotos.objects.filter(model=model, product=product).exists():
            image = VirtualPhotos.objects.get(model=model, product=product)
            return JsonResponse({
                'status': 'done',
                'image': image.photo.url
            })
        else:
            thread = threading.Thread(target=self.idm_vton, args=(model, product))
            thread.start()
            return JsonResponse({
                'status': 'generating'
            })
    def outfit_anyone(self, model, product):
        result = outfit_anyone.predict(
            model_name=handle_file(str(BASE_DIR)+model.model_photo.url),
            garment1=handle_file(str(BASE_DIR)+product.product_image.url),
            garment2=None,
            api_name="/get_tryon_result"
        )
        img_temp = NamedTemporaryFile()
        with open(result, 'rb') as f:
            img_temp.write(f.read())
        img_temp.flush()
        virtual_photo = VirtualPhotos(model=model, product=product)
        virtual_photo.photo.save(
            name=model.model_name + product.product_name,
            content=File(img_temp)
        )
        virtual_photo.save()
    def idm_vton(self, model, product):
        result = IDM_VTON.predict(
            dict={"background":handle_file(str(BASE_DIR)+model.model_photo.url),"layers":[],"composite":None},
            garm_img=handle_file(str(BASE_DIR)+product.product_image.url),
            garment_des="Hello!!",
            is_checked=True,
    		is_checked_crop=True,
            denoise_steps=20,
		    seed=106,
            api_name="/tryon"
        )
        img_temp = NamedTemporaryFile()
        with open(result[0], 'rb') as f:
            img_temp.write(f.read())
        img_temp.flush()
        virtual_photo = VirtualPhotos(model=model, product=product)
        virtual_photo.photo.save(
            name=model.model_name + product.product_name,
            content=File(img_temp)
        )
        virtual_photo.save()

class check_response(View):
    def get(self, request, product_id, model_id):
        model = VirtualModel.objects.get(id=model_id)
        product = ProductItem.objects.get(id=product_id)
        if VirtualPhotos.objects.filter(model=model, product=product).exists():
            image = VirtualPhotos.objects.get(model=model, product=product)
            return JsonResponse({
                'status': 'done',
                'image': image.photo.url
            })
        else:
            return JsonResponse({
                'status': 'generating'
            })