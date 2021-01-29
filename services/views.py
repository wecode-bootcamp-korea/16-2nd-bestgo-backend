import json
import re
import boto3
import my_settings

from django.http        import JsonResponse
from django.views       import View
from django.db.models   import Avg

from datetime           import datetime, timedelta
from users.utils        import login_required
from services.models    import Service, Category, Request, Question
from users.models       import Region, SubRegion, MasterService, Review

class CategoryView(View):
    def get(self, request):
        try:
            all_categories = Category.objects.all()
            category_list  = [{
                            'categoryId'   :category.id,
                            'name'         :category.name,
                            'iconImageUrl' :category.icon_image_url,
                        } for category in all_categories]
            
            return JsonResponse({'Category':category_list}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR_OCCURED'},status=400)
            

class ServiceListView(View):
    def get(self, request):
        try:
            category     = request.GET['catCd']
            cat_id       = Category.objects.get(id=category)

            services     = cat_id.service_set.all()
            service_list = [{
                            'serviceId':service.id,
                            'name'      :service.name,
                            'imageUrl' :service.image_url,
                        } for service in services] 

            return JsonResponse({'CategoryName':cat_id.name,'SeviceList':service_list}, status=200)

        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR_OCCURED'},status=400)

        except ValueError:
            return JsonResponse({'MESSAGE': 'VALUE_ERROR_OCCURED'},status=400)

        except Category.DoesNotExist:
            return JsonResponse({'MESSAGE':'CATEGORY_DOES_NOT_EXISTS'},status=404)
            

class RegionListView(View):
    def get(self, request):
        region_list = [{
                        'name'       : region.name,
                        'subregions' : [subregion.name for subregion in region.subregion_set.all()],
                    } for region in Region.objects.all()]

        return JsonResponse({'Regions':region_list}, status=200)
            
class ServiceDetailView(View):
    @login_required
    def get(self,request):
        try:
            service_id      = request.GET["serviceId"]
            service         = Service.objects.get(id=service_id)
            master_count    = MasterService.objects.filter(service = service_id).count()
            review_count    = Review.objects.filter(service= service_id).count()
            avg_rating      = Review.objects.filter(service= service_id).aggregate(avg=Avg('rating'))
            request_count   = Request.objects.filter(service=service_id).count()
            service_details = {
                    "name"         :service.name,
                    "activeMaster" :master_count,
                    "avgRating"    :round(avg_rating['avg'],1),
                    "totalReview"  :review_count,
                    "totalRequest" :request_count,
            }       

            return JsonResponse({'MESSAGE':'SUCCESS', 'DETAIL':service_details},status= 200)
        
        except Service.DoesNotExist:
            return JsonResponse({'MESSAGE':'SERVICE_DOES_NOT_EXISTS'},status=404)


class QuestionView(View):
    def get(self,request):
        try:
            questions     = Question.objects.all()
            question_list =[{
                "question" : question.name,
                "choices"  : [choices.choice for choices in question.questionchoice_set.all()]
            } for question in questions]

            return JsonResponse({"MESSAGE":"SUCCESS", "QUESTIONS":question_list},status= 200)
        
        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR_OCCURED'},status=400)