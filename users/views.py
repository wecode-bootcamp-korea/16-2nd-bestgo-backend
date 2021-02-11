import json
import bcrypt
import jwt
import re
from datetime               import datetime, timedelta
import requests
from secrets                import token_urlsafe 

from django.http            import JsonResponse
from django.views           import View
from django.core            import mail
from django.template.loader import render_to_string
from django.utils.html      import strip_tags
from django.db.models       import Avg, Count

from my_settings            import SECRET_KEY, ALGORITHM, EMAIL
from users.models           import User, Master, Region, SubRegion, Gender, MasterService
from services.models        import Service, Category
from users.utils            import (
                                    validate_email,
                                    validate_password,
                                    validate_phone_number,
                                    validate_birthdate,
                                    validate_master,
                                    validate_value,
                                    login_required,
                                    master_required,
                                    query_debugger
                            )
                            
class SignUpView(View):

    def post(self, request):
        try:
            data     = json.loads(request.body)
            name     = data['name'] 
            email    = data['email']
            password = data['password']
            
            if User.objects.filter(email=email).exists():
                return JsonResponse({'MESSAGE':'EMAIL_DUPLICATED'}, status=400)

            if not validate_password(password):
                return JsonResponse({'MESSAGE':'INVALID_PASSWORD'}, status=400)

            if not validate_email(email):
                return JsonResponse({'MESSAGE':'INVALID_EMAIL'}, status=400)

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            User.objects.create(
                name  = name,
                email = email,
                password = hashed_password.decode()
            )
            
            return JsonResponse({'MESSAGE':'USER_CREATED'}, status=201)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'JSON_DECODE_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)
        except TypeError:
            return JsonResponse({'MESSAGE': 'TYPE_ERROR'}, status=400)

class SignInView(View):

    def post(self, request):
        try:
            data      = json.loads(request.body)
            email     = data['email']
            password  = data['password']

            if not validate_email(email):
                return JsonResponse({'MESSAGE':'INVALID_EMAIL'}, status=400)

            if not User.objects.filter(email=email).exists():
                return JsonResponse({'MESSAGE':'WRONG_EMAIL'}, status=400)

            user = User.objects.get(email=email)

            if not bcrypt.checkpw(password.encode('utf-8'),user.password.encode('utf-8')):
                return JsonResponse({'MESSAGE':'CHECK_PASSWORD'}, status=400)

            user_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM)
            
            return JsonResponse({'MESSAGE':'SUCCESS', 'TOKEN':user_token}, status=200)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'JSON_DECODE_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)
        except TypeError:
            return JsonResponse({'MESSAGE': 'TYPE_ERROR'}, status=400)

class TempMasterView(View):
    
    def get(self,request):
        master = Master.objects.first()

        master_token = jwt.encode({'master_id':master.id}, SECRET_KEY, algorithm=ALGORITHM)

        return JsonResponse({'MESSAGE': 'MASTER_CREATED','master_token':master_token}, status=201)

class MasterSignUpView(View):

    @login_required
    def post(self, request):
        try:
            data         = json.loads(request.body)
            services     = data['services']
            gender       = Gender.objects.get(name=data['gender'])
            phone_number = data['phone_number']
            birthdate    = data['birthdate']
            region       = Region.objects.get(name=data['region'])
            sub_region   = region.subregion_set.get(name=data['sub_region'])
            user         = getattr(request,'user')
            
            if validate_master(user):
                return JsonResponse({'MESSAGE':'ALREADY_MASTER'}, status=400)

            if not validate_phone_number(phone_number):
                return JsonResponse({'MESSAGE':'INVALID_PHONE_NUMBER'}, status=400)

            if User.objects.filter(phone_number=phone_number).exists():
                 return JsonResponse({'MESSAGE':'DUPLICATED_PHONE_NUMBER'}, status=400)

            if not validate_birthdate(birthdate):
                return JsonResponse({'MESSAGE':'INVALID_BIRTHDATE'}, status=400)

            birthdate         = datetime.strptime(birthdate,'%Y%m%d').date()

            master = Master.objects.create(user=user, birthdate=birthdate, subregions=sub_region)
            MasterService.objects.bulk_create([
                MasterService(master=master, service=Service.objects.get(name=service))
            for service in services ]) 
            
            # master_token      = jwt.encode({'user_id':master.id}, SECRET_KEY, algorithm=ALGORITHM)
            user.phone_number = phone_number
            user.gender       = gender
            user.is_master    = True
            user.save()

            return JsonResponse({'MESSAGE': 'MASTER_CREATED'}, status=201)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'JSON_DECODE_ERROR'}, status=400)
        except Region.DoesNotExist:
            return JsonResponse({'MESSAGE':"REGION_DOSENT_EXIST"} ,status=400)
        except SubRegion.DoesNotExist:
            return JsonResponse({'MESSAGE':"SUBREGION_DOSENT_EXIST"} ,status=400)
        except Gender.DoesNotExist:
            return JsonResponse({'MESSAGE':"GENDER_DOSENT_EXIST"} ,status=400)
        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)
        except TypeError:
            return JsonResponse({'MESSAGE': 'TYPE_ERROR'}, status=400)
        except AttributeError:
            return JsonResponse({'MESSAGE': 'ATTRIBUTE_ERROR'}, status=400)

class CategoryServiceView(View):
    
    def get(self, request):
        try:
            query_strings = request.GET
            
            if query_strings:
                categories = json.loads(request.GET.get('category'))
                offset     = Category.objects.first().id
                services   = Service.objects.filter(category__in=[category+offset for category in categories])
                req_dict   = {
                    'question'     : '구체적으로 어떤 서비스를 진행 할 수 있나요?',
                    'sub_question' : '진행하고자 하는 서비스에 대해 알려주세요. 딱! 맞는 분을 연결 시켜 드릴게요.',
                    'services'     : [ {'name':service.name} for service in services ]
                }
                return JsonResponse(req_dict, status=200)
                
            all_categories = Category.objects.all()
            req_dict       = {
                'question'     : '어떤 서비스를 제공 하실 수 있나요?',
                'sub_question' : '전문적으로 하시는 일을 알려주시면 서비스를 필요로 하는 고객을 연결 시켜 드립니다.',
                'services'   : [ {'id':i, 'name':category.name} for i,category in enumerate(all_categories) ]
            }

            return JsonResponse(req_dict, status=200)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'JSON_DECODE_ERROR'}, status=400)
        except TypeError:
            return JsonResponse({'MESSAGE': 'TYPE_ERROR'}, status=400)
            
class KaKaoView(View):

    def get(self, request):
        try: 
            kakao_token     = request.headers.get('Authorization', None)
            url             = "https://kapi.kakao.com/v2/user/me"
            headers         = {'Authorization': f'Bearer {kakao_token}'}
            kakao_data      = requests.get(url ,headers=headers).json()
            hashed_password = bcrypt.hashpw(token_urlsafe()[:10].encode(), bcrypt.gensalt())
            gender_dict     = {'male':'남자', 'female':'여자'}
            gender          = Gender.objects.get(name=gender_dict[kakao_data['kakao_account']['gender']])
            email           = kakao_data['kakao_account']['email']

            if User.objects.filter(email=email).exists():
                user       = User.objects.get(email=email)
                user_token = jwt.encode({"user_id":user.id}, SECRET_KEY, ALGORITHM)
        
                return JsonResponse({'MESSAGE': 'SUCCESS', 'token':kakao_data}, status=200)

            user = User.objects.create(
                email    = kakao_data['kakao_account']['email'],
                name     = kakao_data['kakao_account']['profile']['nickname'],
                gender   = gender,
                password = hashed_password.decode()
            )
            user_token = jwt.encode({"user_id":user.id}, SECRET_KEY, ALGORITHM)
        
            return JsonResponse({'MESSAGE': 'SUCCESS', 'token':kakao_data}, status=200)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'JSON_DECODE_ERROR'}, status=400)

class PasswordResetView(View):

    def post(self, request):
        try:
            data  = json.loads(request.body)
            email = data['email']

            if not User.objects.filter(email=email).exists():
                return JsonResponse({'MESSAGE': 'EMAIL_DOSENT_EXIST'}, status=400)

            if not validate_email(email):
                return JsonResponse({'MESSAGE':'INVALID_EMAIL'}, status=400)

            user_info    = User.objects.get(email=email)
            expire_date  = datetime.now() + timedelta(days=1)
            token        = jwt.encode(
                {'user_id':user_info.id,'expired_at':str(expire_date)},
                SECRET_KEY,
                algorithm=ALGORITHM
            )
            html_content = render_to_string('email.html',{
                'user_email':email,
                'user_token':f"http://localhost:3000/reset/{token}"
            })

            text_content = strip_tags(html_content)
            msg = mail.EmailMultiAlternatives(
                "Password Reset",
                text_content,
                EMAIL['EMAIL_HOST_USER'],
                [ email ]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return JsonResponse({'MESSAGE': 'EMAIL_SENDED'}, status=200)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'JSON_DECODE_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)
        except TypeError:
            return JsonResponse({'MESSAGE': 'TYPE_ERROR'}, status=400)
        except ValueError:
            return JsonResponse({'MESSAGE': 'VALUE_ERROR'}, status=400)

    def get(self, request):
        try:
            token         = request.headers.get('token',None)
            decoded_token = jwt.decode(
                token,
                SECRET_KEY,
                algorithms = ALGORITHM
            )
            if not User.objects.filter(id=decoded_token['user_id']).exists():
                return JsonResponse({'MESSAGE': 'WRONG_TOKEN', 'valid':False}, status=400)

            if str(datetime.datetime.now()) > decoded_token['expired_at']:
                return JsonResponse({'MESSAGE': 'WRONG_TOKEN', 'valid':False}, status=400)

            return JsonResponse({'MESSAGE': 'SUCCESS', 'valid':True})
        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'JSON_DECODE_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)
        except TypeError:
            return JsonResponse({'MESSAGE': 'TYPE_ERROR'}, status=400)
        except ValueError:
            return JsonResponse({'MESSAGE': 'VALUE_ERROR'}, status=400)
            
    def patch(self, request):
        try:
            data          = json.loads(request.body)
            token         = bytes(data['token'], 'utf-8')
            password      = data['password']

            decoded_token = jwt.decode(
                token,
                SECRET_KEY,
                algorithms = ALGORITHM
            )

            if decoded_token['expired_at'] < str(datetime.now()):
                return JsonResponse({'MESSAGE': 'LINK_EXPIRED'}, status=400)

            user          = User.objects.get(id=decoded_token['user_id'])
            user.password = bcrypt.hashpw(password['resetPassword'].encode(), bcrypt.gensalt()).decode()
            user.save()

            return JsonResponse({'MESSAGE': 'PASSWORD_CHANGED'}, status=200)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'JSON_DECODE_ERROR'}, status=400)
        except KeyError:    
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)
        except TypeError:
            return JsonResponse({'MESSAGE': 'TYPE_ERROR'}, status=400)
        except ValueError:
            return JsonResponse({'MESSAGE': 'VALUE_ERROR'}, status=400)

class ProfileListView(View):
    
    @query_debugger
    def get(self, request):
        sort_method = request.GET.get('sorted_by','id')
        limit       = validate_value(int(request.GET.get('limit',20)))
        offset      = validate_value(int(request.GET.get('offset',0))) 
        masters     = Master.objects.select_related('user')\
                                    .prefetch_related('review_set')\
                                    .annotate(avg=Avg('review__rating'),cnt=Count('review'))\
                                    .order_by(sort_method)[offset:offset+limit]
        master_list = [{
            'id'           : master.id,
            'name'         : master.user.name,
            'introduction' : master.introduction if master.introduction else "",
            'rating'       : round(float(master.avg),1) if master.avg else 0,
            'reviewCount' : master.cnt,
            'review'       : master.review_set.all()[0].content if master.review_set.exists() else "",
            'profileImg'  : master.user.profile_image
        } for master in masters ]

        req_dict = {
            'count'   : masters.count(),
            'masters' : master_list
        }

        return JsonResponse({'masterList':req_dict}, status=200)
        
class ProfileDetailView(View):
    
    @query_debugger
    def get(self, request, master_id):
        try:
            master = Master.objects.select_related('subregions__region')\
                                    .prefetch_related('masterservice_set__service','master_payments')\
                                    .annotate(avg=Avg('review__rating'))\
                                    .get(id=master_id)

            req_dict = [{    
                'name'         : master.user.name,
                'info'         : '본인인증 완료',
                'time'         : '연락 가능 시간 : 오전 6시 ~ 오전 12시',
                'mainService'  : master.masterservice_set.get(is_main=True).service.name\
                                    if master.masterservice_set.filter(is_main=True) else '',
                'introduction' : master.introduction if master.introduction else '',
                'area'         : master.subregions.region.name +" "+ master.subregions.name,
                'rating'       : str(round(float(master.avg),1)),
                'allService'   : [ master_service.service.name for master_service in master.masterservice_set.all() ],
                'description'  : master.description if master.description else '',
                'profileImg'  : master.user.profile_image,
                'payments'     : [ payment.name for payment in master.master_payments.all()]
            }]

            return JsonResponse({'profile': req_dict }, status=200)
        except TypeError:
            return JsonResponse({'MESSAGE': 'TYPE_ERROR'}, status=400)

class ProfileMainServiceView(View):

    @query_debugger
    @master_required
    def get(self, request):
        try: 
            master          = getattr(request,'master')
            master_services = master.masterservice_set.select_related('service').all()

            req_list = [
                master_service.service.name
            for master_service in master_services ]

            return JsonResponse({'services': req_list}, status=200)
        except TypeError:
            return JsonResponse({'MESSAGE': 'TYPE_ERROR'}, status=400)
    
    @master_required
    def patch(self, request):
        try:
            data         = json.loads(request.body)
            main_service = data['main_service']
            master       = getattr(request,'master')
            service      = Service.objects.get(name=main_service)

            master.masterservice_set.all().update(is_main=False)
            master_service         = master.masterservice_set.get(service=service)
            master_service.is_main = True
            master_service.save()
            
            return JsonResponse({'MESSAGE': 'MAIN_SERVICE_CHANGED'}, status=200)
        except Service.DoesNotExist:
            return JsonResponse({'MESSAGE': 'SERVICE_DOESNT_EXIST'}, status=400)
        except TypeError:
            return JsonResponse({'MESSAGE': 'TYPE_ERROR'}, status=400)

class ProfileIntroductionView(View):

    @master_required
    def get(self, request):
        master       = getattr(request,'master')
        introduction = master.introduction if master.introduction else ""

        return JsonResponse({'introduction': introduction}, status=200)
    
    @master_required
    def patch(self, request):
        try:
            data                = json.loads(request.body)
            introduction        = data['introduction']
            master              = getattr(request,'master')
            master.introduction = data['introduction'] if len(introduction)<100 else introduction[:99]
            master.save()

            return JsonResponse({'MESSAGE': 'INTRODUCTION_CHANGED'}, status=200)
        except TypeError:
            return JsonResponse({'MESSAGE': 'TYPE_ERROR'}, status=400)
        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)

class ProfileDescriptionView(View):

    @master_required
    def get(self, request):
        master      = getattr(request,'master')
        description = master.description if master.description else ""

        return JsonResponse({'description': description}, status=200)
    
    @master_required
    def patch(self, request):
        try:
            data               = json.loads(request.body)
            description        = data['description']
            master             = getattr(request,'master')
            master.description = data['description']
            master.save()

            return JsonResponse({'MESSAGE': 'DESCRIPTION_CHANGED'}, status=200)
        except KeyError:
            return JsonResponse({'MESSAGE': 'KEY_ERROR'}, status=400)
