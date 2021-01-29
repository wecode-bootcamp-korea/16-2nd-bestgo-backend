import re, jwt

from django.http  import JsonResponse

from users.models import User
import my_settings

def validate_email(email):
    pattern = re.compile(r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')
    return pattern.match(email)

def validate_password(password):
    return re.findall(r'[0-9]',password) and re.findall(r'[a-zA-Z]',password)

def validate_phone_number(phone_number):
    PHONE_NUMBER_LENGTH = 11
    return (phone_number.isnumeric() and len(phone_number) == PHONE_NUMBER_LENGTH)

def validate_birthdate(birthdate):
    BIRTHDATE_LENGTH = 8
    return (birthdate.isnumeric() and len(birthdate) == BIRTHDATE_LENGTH)

def validate_master(user):
    return user.master_set.exists()

def login_required(function):

    def wrapper(view, request, *args, **kwargs):
        try:
            access_token = request.headers.get("Authorization")

            if not access_token:
                return JsonResponse({'MESSAGE':'LOGIN_REQUIRED'}, status=401)
            
            header = jwt.decode(
                access_token,
                my_settings.SECRET_KEY,
                algorithms=my_settings.ALGORITHM
            )

            if not User.objects.filter(id=header['user_id']).exists():
                return JsonResponse({'MESSAGE':'INVALID_USER'}, status=400)

            setattr(request, "user", User.objects.get(id=header['user_id']))
            return function(view, request, *args, **kwargs)
        except jwt.exceptions.DecodeError:
            return JsonResponse({'MESSAGE': 'JWT_DECODE_ERROR'}, status=400)
    return wrapper