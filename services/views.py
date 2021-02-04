import json
import re
import boto3
import my_settings
from datetime import datetime 

from django.http        import JsonResponse
from django.views       import View
from django.db.models   import Avg

from operator           import itemgetter
from services.utils     import get_date
from datetime           import datetime, timedelta
from users.utils        import login_required
from services.models    import Service, Category, Quotation, Request, RequestMasterMatch, PricingMethod, Question, SelectedChoice, QuestionChoice
from users.models       import Region, SubRegion, MasterService, Review, Master

class CategoryView(View):
    def get(self, request):
        try:
            all_categories = Category.objects.all()
            category_list  = [{
                            'categoryId'   :category.id,
                            'name'         :category.name,
                            'iconImageUrl' :category.icon_image_url,
                        } for category in all_categories]
            
            return JsonResponse({"Category":category_list}, status=200)

        except KeyError:
            return JsonResponse({"MESSAGE": "KEY_ERROR_OCCURED"},status=400)
            

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

            return JsonResponse({'CategoryName':cat_id.name,'ServiceList':service_list}, status=200)

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
            if not avg_rating['avg']:
                ratings     = 0
            else:
                ratings     = float(round(avg_rating['avg'],1))
            
            service_details = {
                    "name"         :service.name,
                    "activeMaster" :master_count,
                    "avgRating"    :ratings,
                    "totalReview"  :review_count,
                    "totalRequest" :request_count,
            }       

            return JsonResponse({'MESSAGE':'SUCCESS', 'DETAIL':service_details},status= 200)
        
        except Service.DoesNotExist:
            return JsonResponse({'MESSAGE':'SERVICE_DOES_NOT_EXISTS'},status=404)


class QuestionView(View):
    def get(self,request):
        questions     = Question.objects.all()
        question_list =[{
            "question" : question.name,
            "choices"  : [choices.choice for choices in question.questionchoice_set.all()]
        } for question in questions]

        return JsonResponse({"QUESTIONS":question_list},status= 200)


class RequestView(View):
    @login_required
    def post(self, request):
        try:
            data          = json.loads(request.body)
            which_user    = getattr(request,'user')
            service_id    = request.GET['serviceId']
            which_service = Service.objects.get(id=service_id)
            which_region  = SubRegion.objects.get(name=data["region"])
            new_request   = Request.objects.create(
                user       = which_user,
                service    = which_service,
                subregion  = which_region,
                expired_at = datetime.now()+timedelta(days=7),
            )

            for chosen in data['choices']:
                SelectedChoice.objects.create(
                    request = new_request,
                    choice  = QuestionChoice.objects.get(choice=chosen),
                    )

            return JsonResponse({'MESSAGE':'REQUEST_MADE_SUCCESSFUL',"requestId":new_request.id},status= 200)
       
        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR_OCCURED'},status=400)
        except Service.DoesNotExist:
            return JsonResponse({'MESSAGE':'SERVICE_DOES_NOT_EXISTS'},status=404)


class RequestDistributionView(View):
    def post(self, request):
        try:
            service_id      = request.GET['serviceId']
            request_id      = request.GET['requestId']
            which_service   = Service.objects.get(id=service_id)
            which_request   = Request.objects.get(id=request_id)
            master_services = MasterService.objects.filter(service = which_service)
            
            priority_count = 0
            for candidate in master_services:
                if candidate.master.subregions == which_request.subregion:
                    priority_count += 2
                if candidate.master.subregions.region == which_request.subregion.region:
                    priority_count += 1
                if candidate.is_main:
                    priority_count += 1
                if candidate.master.user.gender == which_request.choices.get(question_id=2):
                    priority_count += 1

                RequestMasterMatch.objects.create(
                    request  = which_request,
                    master   = candidate.master,
                    priority = priority_count,
                )
            matches_count = RequestMasterMatch.objects.filter(request=which_request).count()

            return JsonResponse({'MESSAGE':'REQUEST_MATCHED_SUCCESSFUL', 'Matched_Master':matches_count},status= 200)
    
        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR_OCCURED'},status=400)
        except Service.DoesNotExist:
            return JsonResponse({'MESSAGE':'SERVICE_DOES_NOT_EXISTS'},status=404)
        except Request.DoesNotExist:
            return JsonResponse({'MESSAGE':'REQUEST_DOES_NOT_EXISTS'},status=404)

class ReceivedRequestListView(View):
    @login_required
    def get(self, request):
        which_user     = getattr(request,'user')
        master         = Master.objects.get(user=which_user)
        received_all   = RequestMasterMatch.objects.filter(master=master)
        received_lists =[]

        for received in received_all:
            question_choices = received.request.selectedchoice_set.all()
            choices_string   = ''
            for choice in question_choices:
                choices_string += str(choice.choice.choice)+','
            create_time = received.request.created_at
            expire_date = received.request.expired_at
            now         = datetime.now()
            is_expired  = now.date() < expire_date.date()
            full_region = received.request.subregion.region.name+' '+received.request.subregion.name
            
            each_request = {
                'requestId'      : received.request.id,
                'requester'      : received.request.user.name,
                'requesterImage' : received.request.user.profile_image,
                'service'        : received.request.service.name,
                'region'         : full_region,
                'choices'        : choices_string,
                'expiredAt'      : is_expired,
                'timeAgo'        : get_date(create_time),
                'createdAt'      : received.request.created_at,
            }
            received_lists.append(each_request)
            received_list = sorted(received_lists, key=itemgetter('createdAt'), reverse =True)
    
        return JsonResponse({'receivedRequests':received_list},status= 200)
    

class ReceivedRequestDetailView(View):
    def get(self, request):
        try:
            which_request = request.GET['requestId']
            request       = Request.objects.get(id=which_request)
            full_region   = request.subregion.region.name+' '+request.subregion.name
            match         = RequestMasterMatch.objects.filter(request = request).count()
            request_detail = [{
                    'requester'           : request.user.name,
                    'requesterImage'      : request.user.profile_image,
                    'service'             : request.service.name,
                    'region'              : full_region,
                    'receivedQuotations'  : match,
                }
            ]
            questions     = SelectedChoice.objects.filter(request=request)
            question_list =[{
                "question": question.choice.question.name,
                "choice"  : question.choice.choice,
            } for question in questions]
            details       = request_detail+question_list

            return JsonResponse({'requestDetail':details},status= 200)
            
        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR_OCCURED'},status=400)    
        except Request.DoesNotExist:
            return JsonResponse({'MESSAGE':'REQUEST_DOES_NOT_EXISTS'},status=404)

class QuotationView(View):
    @login_required
    def post(self, request):
        try:
            data          = json.loads(request.body)
            which_request = request.GET['requestId']
            which_user    = getattr(request,'user')
            which_master  = Master.objects.get(user=which_user)
            matched       = RequestMasterMatch.objects.get(request=which_request, master=which_master)
            which_method  = PricingMethod.objects.get(name=data['pricingMethod'])
            Quotation.objects.create(
                match          = matched,
                price          = data['price'],
                pricing_method = which_method,
            )

            return JsonResponse({"MESSAGE":"QUOTATION_SENT"},status= 200)
        
        except KeyError:
            return JsonResponse({"MESSAGE": "KEY_ERROR_OCCURED"},status=400)    
        
        except Request.DoesNotExist:
            return JsonResponse({"MESSAGE":"REQUEST_DOES_NOT_EXISTS"},status=404)


class QuotationListView(View):
    @login_required
    def get(self,request):
        try:
            which_user    = getattr(request,'user')
            made_requests = Request.objects.filter(user=which_user)
            users_quotations=[]
            for request in made_requests:
                is_expired     = datetime.now().date() >= request.expired_at.date()
                matched_master = RequestMasterMatch.objects.filter(request=request)

                all_quotations = {
                    'requestId'    : request.id,
                    'service'      : request.service.name,
                    'createdAt'   : request.created_at.date(),
                    'expired'      : is_expired,
                    'masterImage' : [{
                        'masterId'           : profile.master.id,
                        'masterImageUrl'     : profile.master.user.profile_image,
                    } for profile in matched_master]
                }
                users_quotations.append(all_quotations)
            return JsonResponse({'allQuotations':users_quotations},status= 200)

        except KeyError:
            return JsonResponse({"MESSAGE": "KEY_ERROR_OCCURED"},status=400)