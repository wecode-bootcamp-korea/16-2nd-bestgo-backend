import json
import bcrypt
import jwt
import re
from datetime               import datetime, timedelta

from django.http            import JsonResponse
from django.views           import View
from django.core            import mail
from django.template.loader import render_to_string
from django.utils.html      import strip_tags

from my_settings            import SECRET_KEY, ALGORITHM, EMAIL
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
            
class KaKaoView(View):

    def get(self, request):
        try: 
            kakao_token     = request.headers.get('Authorization', None)
            url             = "https://kapi.kakao.com/v2/user/me"
            headers         = {'Authorization': f'Bearer {kakao_token}'}
            kakao_data      = requests.get(url ,headers=headers).json()
            hashed_password = bcrypt.hashpw(token_urlsafe()[:10].encode(), bcrypt.gensalt())
            gender_dict     = {'male':'남자', 'female':'여자'}
            gender          = Gender.objects.get(name=gender_dict[kakao_data['kakao_account']['profile']['gender']])

            user, created = User.objects.get_or_create(
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
