import unittest, json, jwt
import bcrypt
from datetime        import datetime
from secrets         import token_urlsafe
from unittest.mock   import MagicMock, patch

from django.test     import TestCase,Client, TransactionTestCase

from users.models    import User, Gender, Region, SubRegion, Master, MasterService
from services.models import Service, Category
from my_settings     import SECRET_KEY, ALGORITHM

client = Client()

class UserSignUpSignInTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        hashed_password = bcrypt.hashpw('1a2s3d4f'.encode('utf-8'), bcrypt.gensalt())
        User.objects.create(
            name     = '장장장',
            email    = 'jun1714@mail.com',
            password = hashed_password.decode()
        )

    def setUp(self):
        pass

    def test_user_post_signup_success(self):
        user = {
            'name'    :'장장장',
            'password':'1a2s3d4f',
            'email'   :'jun17@mail.com'
        }

        response = client.post('/users/signup', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),{
            'MESSAGE':'USER_CREATED'
        })

    def test_user_post_signup_email_duplicate(self):
        user = {
            'name'    :'장장장',
            'password':'1a2s3d4f',
            'email'   :'jun1714@mail.com'
        }

        response = client.post('/users/signup', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'EMAIL_DUPLICATED'
        })

    def test_user_post_signup_invalid_email(self):
        user = {
            'name'    :'장장장',
            'password':'1a2s3d4f',
            'email'   :'jun17114mailcom'
        }

        response = client.post('/users/signup', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'INVALID_EMAIL'
        })

    def test_user_post_signup_invalid_password(self):
        user = {
            'name'    :'장장장',
            'password':'asdfqwer',
            'email'   :'jun17@mail.com'
        }

        response = client.post('/users/signup', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'INVALID_PASSWORD'
        })

    def test_user_post_signup_key_error(self):
        user = {
            'name'    :'장장장',
            'password':'1a2s3d4f'
        }

        response = client.post('/users/signup', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'KEY_ERROR'
        })
    
    def test_user_post_signup_type_error(self):
        user = {
            'name'    :'장장장',
            'password':'1a2s3d4f',
            'email'   :1231234
        }

        response = client.post('/users/signup', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'TYPE_ERROR'
        })

    def test_user_post_signin_success(self):
        user = {
            'email'   : 'jun1714@mail.com',
            'password':'1a2s3d4f'
        }

        response = client.post('/users/signin', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),{
            'MESSAGE':'SUCCESS',
            'TOKEN':response.json()['TOKEN']
        })

    def test_user_post_signin_invalid_email(self):
        client = Client()
        user = {
            'email'   : 'jun1714mailcom',
            'password':'1a2s3d4f'
        }

        response = client.post('/users/signin', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'INVALID_EMAIL',
        })
    
    def test_user_post_signin_wrong_email(self):
        client = Client()
        user = {
            'email'   : 'jun1714124@mail.com',
            'password':'1a2s3d4f'
        }

        response = client.post('/users/signin', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'WRONG_EMAIL',
        })

    def test_user_post_signin_wrong_password(self):
        client = Client()
        user = {
            'email'   : 'jun1714@mail.com',
            'password':'1a2s3d4fa'
        }

        response = client.post('/users/signin', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'CHECK_PASSWORD',
        })
    
    def test_user_post_signin_key_error(self):
        client = Client()
        user = {
            'email'   : 'jun1714@mail.com',
        }

        response = client.post('/users/signin', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'KEY_ERROR',
        })
    
    def test_user_post_signin_type_error(self):
        client = Client()
        user = {
            'email'   : 1234,
            'password':'1a2s3d4f'
        }

        response = client.post('/users/signin', json.dumps(user), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'TYPE_ERROR',
        })

class MasterSignUpTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        hashed_password = bcrypt.hashpw('1a2s3d4f'.encode('utf-8'), bcrypt.gensalt())
        user = User.objects.create(
            name         = '장장장',
            email        = 'jun553714@mail.com',
            password     = hashed_password.decode(),
            phone_number = '01315232919'
        )
        gender     = Gender.objects.create(name='남자')
        region     = Region.objects.create(name='서울특별시')
        SubRegion.objects.create(name='광진구', region=region)
        sub_region = region.subregion_set.get(name='광진구')
        category   = Category.objects.create(name='백엔드')
        service    = Service.objects.create(category=category, name='Python')
        birthdate  = datetime.strptime('18231103', '%Y%m%d').date()
        master     = Master.objects.create(
            user       = user,
            birthdate  = birthdate,
            subregions = sub_region 
        )
        MasterService.objects.create(
                master  = master,
                service = service
        )    

    def setUp(self):
        pass
        
    def test_master_signup_success(self):
        user = User.objects.create(
            name         = '장장장',
            email        = 'ju1234@mail.com',
            password     = '1a2s3d4d'
        )
        master = {
            "gender":"남자",
            "phone_number":"01038233323",
            "region":"서울특별시",
            "sub_region":"광진구",
            "birthdate":"19991023",
            "services":['Python']
        }
        user_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM)
        response   = client.post('/users/master_signup', json.dumps(master), **{"HTTP_Authorization" : user_token}, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),{
            'MESSAGE':'MASTER_CREATED'
        })

    def test_master_signup_invalid_birthdate(self):
        user = User.objects.create(
            name         = '장장장',
            email        = 'ju1234@mail.com',
            password     = '1a2s3d4d'
        )

        master = {
            'gender':'남자',
            'phone_number':'01038233323',
            'region':'서울특별시',
            'sub_region':'광진구',
            'birthdate':'1812110',
            'services':['Python']
        }
        user_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM)
        response   = client.post('/users/master_signup', json.dumps(master), **{"HTTP_Authorization" : user_token}, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'INVALID_BIRTHDATE'
        })

    def test_master_signup_invalid_phone_number(self):
        user = User.objects.create(
            name         = '장장장',
            email        = 'ju1234@mail.com',
            password     = '1a2s3d4d'
        )

        master = {
            'gender':'남자',
            'phone_number':'0103233323',
            'region':'서울특별시',
            'sub_region':'광진구',
            'birthdate':'18121110',
            'services':['Python']
        }
        user_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM)
        response   = client.post('/users/master_signup', json.dumps(master), **{"HTTP_Authorization" : user_token}, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'INVALID_PHONE_NUMBER'
        })

    def test_master_signup_attribute_error(self):
        user = User.objects.create(
            name         = '장장장',
            email        = 'ju1234@mail.com',
            password     = '1a2s3d4d'
        )

        master = {
            'gender':'남자',
            'phone_number':123,
            'region':'서울특별시',
            'sub_region':'광진구',
            'birthdate':'1812110',
            'services':['Python']
        }
        user_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM)
        response   = client.post('/users/master_signup', json.dumps(master), **{"HTTP_Authorization" : user_token}, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'ATTRIBUTE_ERROR'
        })
    
    def test_master_signup_type_error(self):
        user = User.objects.create(
            name         = '장장장',
            email        = 'ju1234@mail.com',
            password     = '1a2s3d4d'
        )

        master = {
            'gender':'남자',
            'phone_number':'01038233323',
            'region':'서울특별시',
            'sub_region':'광진구',
            'birthdate':'18121110',
            'services':123
        }
        user_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM)
        response   = client.post('/users/master_signup', json.dumps(master), **{"HTTP_Authorization" : user_token}, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'TYPE_ERROR'
        })

    def test_master_signup_key_error(self):
        user = User.objects.create(
            name         = '장장장',
            email        = 'ju1234@mail.com',
            password     = '1a2s3d4d'
        )

        master = {
            'phone_number':'01038233323',
            'region':'서울특별시',
            'sub_region':'광진구',
            'birthdate':'18121110',
            'services':123
        }
        user_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM)
        response   = client.post('/users/master_signup', json.dumps(master), **{"HTTP_Authorization" : user_token}, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'KEY_ERROR'
        })

    def test_master_signup_sub_region_does_not_exist(self):
        user = User.objects.create(
            name         = '장장장',
            email        = 'ju1234@mail.com',
            password     = '1a2s3d4d'
        )

        master = {
            'gender':'남자',
            'phone_number':'01038233323',
            'region':'서울특별시',
            'sub_region':'asdf',
            'birthdate':'18121110',
            'services':['Python']
        }
        user_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM)
        response   = client.post('/users/master_signup', json.dumps(master), **{"HTTP_Authorization" : user_token}, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'SUBREGION_DOSENT_EXIST'
        })

    def test_master_signup_region_does_not_exist(self):
        user = User.objects.create(
            name         = '장장장',
            email        = 'ju1234@mail.com',
            password     = '1a2s3d4d'
        )

        master = {
            'gender':'남자',
            'phone_number':'01038233323',
            'region':'asdf',
            'sub_region':'광진구',
            'birthdate':'18121110',
            'services':['Python']
        }
        user_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM)
        response   = client.post('/users/master_signup', json.dumps(master), **{"HTTP_Authorization" : user_token}, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'REGION_DOSENT_EXIST'
        })

    def test_master_signup_gender_does_not_exist(self):
        user = User.objects.create(
            name         = '장장장',
            email        = 'ju1234@mail.com',
            password     = '1a2s3d4d'
        )

        master = {
            'gender':'비빔밥',
            'phone_number':'01038233323',
            'region':'서울틐별시',
            'sub_region':'광진구',
            'birthdate':'18121110',
            'services':['Python']
        }
        user_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM)
        response   = client.post('/users/master_signup', json.dumps(master), **{"HTTP_Authorization" : user_token}, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'GENDER_DOSENT_EXIST'
        })
    
    def test_master_signup_master_already_exist(self):
        user = User.objects.create(
            name         = '장장장',
            email        = 'ju1234@mail.com',
            password     = '1a2s3d4d'
        )

        master = {
            'gender':'남자',
            'phone_number':'01038233323',
            'region':'서울특별시',
            'sub_region':'광진구',
            'birthdate':'18121110',
            'services':['Python']
        }
        user_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM)
        response   = client.post('/users/master_signup', json.dumps(master), **{"HTTP_Authorization" : user_token}, content_type='application/json')
        response   = client.post('/users/master_signup', json.dumps(master), **{"HTTP_Authorization" : user_token}, content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'ALREADY_MASTER'
        })

class CategoryView(TransactionTestCase):

    def Setup(self):
        category = Category.objects.create(name='프런트엔드')
        Service.objects.create(name='HTML', category=category)
        Service.objects.create(name='CSS', category=category)
        Service.objects.create(name='React', category=category)

    def tearDown(self):
        SubRegion.objects.all().delete()
        Region.objects.all().delete()

    def test_get_category_service_success(self):
        category = Category.objects.create(name='프런트엔드')
        Service.objects.create(name='HTML', category=category)
        Service.objects.create(name='CSS', category=category)
        Service.objects.create(name='React', category=category)

        response = client.get('/users/category',{'category': '[2]'}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),{
            "services": [
                "HTML",
                "CSS",
                "React"
            ]
        })

    def test_get_category_service_type_error(self):
        category = Category.objects.create(name='프런트엔드')
        Service.objects.create(name='HTML', category=category)
        Service.objects.create(name='CSS', category=category)
        Service.objects.create(name='React', category=category)

        response = client.get('/users/category',{'category': [2]}, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
            'MESSAGE':'TYPE_ERROR'
        })

class KakaoSignInTest(TestCase):

    def setUp(self):
        hashed_password = bcrypt.hashpw(token_urlsafe()[:10].encode(), bcrypt.gensalt())
        kakao_data      = {
            'kakao_account': {
                'email' : 'jang@kakao.com',
                'profile' : {
                    'nickname' : 'hi',
                    'gender'   : '남자'
                }
            }
        }
        Gender.objects.create(name='남자')
        gender = Gender.objects.get(name=kakao_data['kakao_account']['profile']['gender'])
        User.objects.create(
            email    = kakao_data['kakao_account']['email'],
            name     = kakao_data['kakao_account']['profile']['nickname'],
            gender   = gender,
            password = hashed_password.decode()
        )
    
    def tearDown(self):
        User.objects.all().delete()

    @patch('users.views.requests')
    def test_kakao_signin_success(self, mock_request):

        class FakeResponse:
            def json(self):
                return { 'kakao_account': {
                            'email' : 'jang41@kakao.com',
                            'profile' : {
                                'nickname' : 'hi',
                                'gender'   : 'male'
                            }
                        }}
        mock_request.get = MagicMock(return_value = FakeResponse())
        header           = {'Authorization': 'fake'}
        response         = client.get('/users/kakao_signin', **header, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),{
            'MESSAGE':'SUCCESS',
            'token':response.json()['token']
        })
