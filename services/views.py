import json
import re
from django.http             import JsonResponse
from django.views            import View

from services.models          import Service, Category

class CategoryView(View):
    def get(self, request):
        try:
            all_categories = Category.objects.all()
            category_list = [{
                            'category_id'    :category.id,
                            'name'           :category.name,
                            'icon_image_url' :category.icon_image_url,
                        } for category in all_categories]
            
            return JsonResponse({'RESULT':category_list}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR_OCCURED'},status=400)
            

class ServiceListView(View):
    def get(self, request):
        try:
            category = request.GET['catCd']
            cat_id   = Category.objects.get(id=category)

            services = cat_id.service_set.all()
            service_list = [{
                            'service_id':service.id,
                            'name'      :service.name,
                            'image_url' :service.image_url,
                        } for service in services] 

            return JsonResponse({'Category':cat_id.name,'RESULT':service_list}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR_OCCURED'},status=400)

        except ValueError:
            return JsonResponse({'MESSAGE': 'VALUE_ERROR_OCCURED'},status=400)

        except Category.DoesNotExist:
            return JsonResponse({'MESSAGE':'CATEGORY_DOES_NOT_EXISTS'},status=404)
            
