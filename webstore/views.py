from io import BytesIO
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

class UserTryonView(View):
    def get(self, request, product_id):
        product = ProductItem.objects.get(id=product_id)
        context = {}
        context['product'] = product
        return render(request, 'webstore/user_tryon.html', context)
    
    def post(self, request, product_id):
        user_profile = request.user.userprofile  # Assumes authentication

        if 'user_image' not in request.FILES:
            return JsonResponse({'status': 'error', 'message': 'No user image provided.'}, status=400)

        product = ProductItem.objects.get(id=product_id)
        uploaded_file = request.FILES['user_image']

        # ✅ Delete existing UserPhotos (if any)
        UserPhotos.objects.filter(user=user_profile, product=product).delete()

        # ✅ Copy uploaded file into memory before thread
        image_data = BytesIO(uploaded_file.read())
        image_data.name = uploaded_file.name
        image_data.content_type = uploaded_file.content_type

        thread = threading.Thread(
            target=self.user_vton,
            args=(user_profile, image_data, product)
        )
        thread.start()

        return JsonResponse({'status': 'generating'})

    def user_vton(self, user_profile, image_data, product):
        # ✅ Write uploaded image to temp file
        temp_image = NamedTemporaryFile()
        temp_image.write(image_data.read())
        temp_image.flush()

        # ✅ Run the virtual try-on engine
        result = IDM_VTON.predict(
            dict={
                "background": handle_file(temp_image.name),
                "layers": [],
                "composite": None
            },
            garm_img=handle_file(str(BASE_DIR) + product.product_image.url),
            garment_des="Hello!!",
            is_checked=True,
            is_checked_crop=True,
            denoise_steps=20,
            seed=106,
            api_name="/tryon"
        )

        # ✅ Save generated result to another temp file
        img_temp = NamedTemporaryFile()
        with open(result[0], 'rb') as f:
            img_temp.write(f.read())
        img_temp.flush()

        # ✅ Create new UserPhotos instance (old one was deleted earlier)
        user_photo = UserPhotos(user=user_profile, product=product)
        user_photo.photo.save(
            name=f"{user_profile.user.username}_{product.product_name}.jpg",
            content=File(img_temp)
        )
        user_photo.save()

class UserTryonPollView(View):
    def get(self, request, product_id):
        user_profile = request.user.userprofile  # Assumes the user is authenticated
        try:
            user_photo = UserPhotos.objects.get(user=user_profile, product__id=product_id)
            return JsonResponse({
                'status': 'done',
                'image': user_photo.photo.url
            })
        except UserPhotos.DoesNotExist:
            return JsonResponse({
                'status': 'generating'
            })

class UserCustomTryonView(View):
    def get(self, request):
        return render(request, 'webstore/wardrobe.html')

    def post(self, request):
        user_profile = request.user.userprofile

        user_file = request.FILES.get('user_image')
        product_file = request.FILES.get('product_image')

        if not user_file or not product_file:
            return JsonResponse({'status': 'error', 'message': 'Both user and product images are required.'}, status=400)

        # Copy files into memory
        user_image_data = BytesIO(user_file.read())
        user_image_data.name = user_file.name
        user_image_data.content_type = user_file.content_type

        product_image_data = BytesIO(product_file.read())
        product_image_data.name = product_file.name
        product_image_data.content_type = product_file.content_type

        # ✅ Run everything in a thread, including predict
        thread = threading.Thread(
            target=self.run_full_pipeline_threaded,
            args=(user_profile, user_image_data, product_image_data)
        )
        thread.start()

        return JsonResponse({'status': 'generating'})

    def run_full_pipeline_threaded(self, user_profile, user_image_data, product_image_data):
        try:
            # Write images to temp files
            temp_user = NamedTemporaryFile()
            temp_user.write(user_image_data.read())
            temp_user.flush()

            temp_product = NamedTemporaryFile()
            temp_product.write(product_image_data.read())
            temp_product.flush()

            # ✅ Run predict inside thread (blocking version)
            result = IDM_VTON.predict(
                dict={
                    "background": handle_file(temp_user.name),
                    "layers": [],
                    "composite": None
                },
                garm_img=handle_file(temp_product.name),
                garment_des="Custom Upload",
                is_checked=True,
                is_checked_crop=True,
                denoise_steps=20,
                seed=106,
                api_name="/tryon"
            )

            # Save output
            self.save_to_wardrobe(user_profile, result)

        except Exception as e:
            # Optional: log this error
            print("Threaded VTON pipeline error:", str(e))

    def save_to_wardrobe(self, user_profile, result):
        img_temp = NamedTemporaryFile()
        with open(result[0], 'rb') as f:
            img_temp.write(f.read())
        img_temp.flush()

        wardrobe_item = Wardrobe(user=user_profile)
        wardrobe_item.photo.save(
            name=f"{user_profile.user.username}_wardrobe.jpg",
            content=File(img_temp)
        )
        wardrobe_item.save()

class WardrobePollView(View):
    def get(self, request):
        user_profile = request.user.userprofile
        try:
            latest_item = Wardrobe.objects.filter(user=user_profile).latest('id')
            return JsonResponse({
                'status': 'done',
                'image': latest_item.photo.url
            })
        except Wardrobe.DoesNotExist:
            return JsonResponse({'status': 'generating'})
