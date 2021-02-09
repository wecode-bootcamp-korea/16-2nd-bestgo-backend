import re, jwt
import functools, time

from django.http  import JsonResponse
from django.db   import connection, reset_queries

from users.models import User, Master
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

def master_required(function):

    def wrapper(view, request, *args):
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
            
            user = User.objects.get(id=header['user_id'])

            if not user.is_master:
                return JsonResponse({'MESSAGE':'MASTER_REQUIRED'}, status=401)

            setattr(request, 'master', Master.objects.get(user=user))
            return function(view, request, *args)
        except jwt.exceptions.DecodeError:
            return JsonResponse({'MESSAGE': 'JWT_DECODE_ERROR'}, status=400)
    return wrapper

def query_debugger(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        reset_queries()
        number_of_start_queries = len(connection.queries)
        start  = time.perf_counter()
        result = func(*args, **kwargs)
        end    = time.perf_counter()
        number_of_end_queries = len(connection.queries)
        print(f"-------------------------------------------------------------------")
        print(f"Function : {func.__name__}")
        print(f"Number of Queries : {number_of_end_queries-number_of_start_queries}")
        print(f"Finished in : {(end - start):.2f}s")
        print(f"-------------------------------------------------------------------")
        return result
    return wrapper

def validate_value(input_int):
    max_length = Master.objects.count()

    if input_int > max_length:
        return max_length
    elif input_int < 0:
        return 0
    
    return input_int