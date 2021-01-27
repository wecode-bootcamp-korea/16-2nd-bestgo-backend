import json
import bcrypt
import jwt
import re
from datetime               import datetime 

from django.http            import JsonResponse
from django.views           import View

from my_settings            import SECRET_KEY, ALGORITHM
from users.models           import User, Master, Region, SubRegion, Gender, MasterService
from services.models        import Service, Category
from users.utils            import (
                                    validate_email,
                                    validate_password,
                                    validate_phone_number,
                                    validate_birthdate,
                                    validate_master,
                                    login_required
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

            if not validate_birthdate(birthdate):
                return JsonResponse({'MESSAGE':'INVALID_BIRTHDATE'}, status=400)

            birthdate         = datetime.strptime(birthdate,'%Y%m%d').date()
            user.phone_number = phone_number
            user.save()

            master = Master.objects.create(user=user, birthdate=birthdate, subregions=sub_region)
            MasterService.objects.bulk_create([
                MasterService(master=master, service=Service.objects.get(name=service))
            for service in services ]) 
            
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
                services   = Service.objects.filter(category__in=categories)
                req_list   = [ service.name for service in services ]

                return JsonResponse({'services': req_list }, status=200)
                
            all_categories = Category.objects.all()
            req_list       = [ category.name for category in all_categories]

            return JsonResponse({'categories': req_list }, status=200)
        except json.decoder.JSONDecodeError:
            return JsonResponse({'MESSAGE': 'JSON_DECODE_ERROR'}, status=400)
        except TypeError:
            return JsonResponse({'MESSAGE': 'TYPE_ERROR'}, status=400)
