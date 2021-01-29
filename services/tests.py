from django.test     import TestCase, Client, TransactionTestCase
from unittest.mock   import patch, MagicMock
from services.models import Category, Service, Question, QuestionChoice, Request
from users.models    import Review, MasterService, User, Gender, Region, SubRegion, Master
from datetime        import datetime, timedelta
from my_settings     import SECRET_KEY, ALGORITHM
 

import bcrypt
import json
import jwt

client = Client()
class CategoryViewTest(TransactionTestCase):
    reset_sequences = True
    def setUp(self):
        Category.objects.create(
            name           = 'Test1',
            icon_image_url = 'test_icon.url1'
        )
        Category.objects.create(
            name           = 'Test2',
            icon_image_url = 'test_icon.url2'
        )
        Category.objects.create(
            name           = 'Test3',
            icon_image_url = 'test_icon.url3'
        )
        
    def tearDown(self):
        Category.objects.all().delete()

    def test_all_category_get_success(self):
        response = client.get('/services/categories', HTTP_ACCEPT='application/json')
        
        self.assertEqual(
            response.json(),{ 
                "RESULT": [
                    {
                        'categoryId'   :1,
                        'name'         :'Test1',
                        'iconImageUrl' :'test_icon.url1',              
                    },
                    {
                        'categoryId'   :2,
                        'name'         :'Test2',
                        'iconImageUrl' :'test_icon.url2',              
                    },
                    {
                        'categoryId'   :3,
                        'name'         :'Test3',
                        'iconImageUrl' :'test_icon.url3',              
                    },
                ]
            }
        )
        self.assertEqual(response.status_code, 200)


class ServiceListViewTest(TransactionTestCase):
    reset_sequences = True
    def setUp(self):
        cat_id = Category.objects.create(
            name           = 'Test',
            icon_image_url = 'test_icon.url'
        )
        
        Service.objects.create(
            category  = cat_id,
            name      = 'test1',
            image_url = 'test.url1',
        )
        Service.objects.create(
            category  = cat_id,
            name      = 'test2',
            image_url = 'test.url2'
        )

    def tearDown(self):
        Category.objects.all().delete()
        Service.objects.all().delete()

    def test_servicelist1_response_success(self):
        response = client.get('/services/services',{'catCd': 1}, HTTP_ACCEPT='application/json')
        self.assertEqual(
            response.json(),{ 
                "Category": "Test",
                "RESULT": [
                    {
                        'serviceId' :1,
                        'name'      :'test1',
                        'imageUrl'  :'test.url1',              
                    },
                    {
                        'serviceId' :2,
                        'name'      :'test2',
                        'imageUrl'  :'test.url2',              
                    },
                ]
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_servicelist2_response_category_does_not_exist_fail(self):
        response = client.get('/services/services',{'catCd':99}, HTTP_ACCEPT='application/json')
        self.assertEqual(response.json(),
            {
                "MESSAGE": "CATEGORY_DOES_NOT_EXISTS"
            }
        )
        self.assertEqual(response.status_code, 404)


class QuestionViewTest(TransactionTestCase):
    reset_sequences = True
    def setUp(self):
        question1 = Question.objects.create(name='TestQuestion1')
        question2 = Question.objects.create(name='TestQuestion2')
        QuestionChoice.objects.create(
            question = question1,
            choice   = 'TestChoice1-1'
        )
        QuestionChoice.objects.create(
            question = question1,
            choice   = 'TestChoice1-2'
        )
        QuestionChoice.objects.create(
            question = question1,
            choice   = 'TestChoice1-3'
        )
        QuestionChoice.objects.create(
            question = question2,
            choice   = 'TestChoice2-1'
        )
        QuestionChoice.objects.create(
            question = question2,
            choice   = 'TestChoice2-2'
        )
        QuestionChoice.objects.create(
            question = question2,
            choice   = 'TestChoice2-3'
        )

    def tearDown(self):
        Question.objects.all().delete()
        QuestionChoice.objects.all().delete()

    def test_all_questions_get_success(self):
        response = client.get('/services/questions', HTTP_ACCEPT='application/json')
        
        self.assertEqual(
            response.json(),{ 
                "MESSAGE": "SUCCESS",
                "QUESTIONS": [
                    {
                        "question" : "TestQuestion1",
                        "choices"  : [
                            "TestChoice1-1",
                            "TestChoice1-2",
                            "TestChoice1-3",
                        ],              
                    },
                    {
                        "question" : "TestQuestion2",
                        "choices"  : [
                            "TestChoice2-1",
                            "TestChoice2-2",
                            "TestChoice2-3",
                        ],              
                    },
                ]
            }
        )
        self.assertEqual(response.status_code, 200)


class ServiceDetailViewTest(TransactionTestCase):
    reset_sequences = True
    def setUp(self):
        hashed_password = bcrypt.hashpw('1a2s3d4f'.encode('utf-8'), bcrypt.gensalt())
        user_test1 = User.objects.create(
            name         = '유저일',
            email        = 'test1@mail.com',
            password     = hashed_password.decode(),
            phone_number = '01315232919'
        )
        user_test2 = User.objects.create(
            name         = '유저이',
            email        = 'test2@mail.com',
            password     = hashed_password.decode(),
            phone_number = '01315232918'
        )
        gender       = Gender.objects.create(name='남자')
        region       = Region.objects.create(name='서울특별시')
        SubRegion.objects.create(name='광진구', region=region)
        sub_region   = region.subregion_set.get(name='광진구')
        category     = Category.objects.create(name='TestCategory')
        service      = Service.objects.create(category=category, name='TestService')
        birthdate    = datetime.strptime('18231103', '%Y%m%d').date()
        master_test1 = Master.objects.create(
            user       = user_test1,
            birthdate  = birthdate,
            subregions = sub_region
        )
        master_test2 = Master.objects.create(
            user       = user_test2,
            birthdate  = birthdate,
            subregions = sub_region
        )
        master_service1 = MasterService.objects.create(
                master  = master_test1,
                service = service
        )
        master_service2 = MasterService.objects.create(
                master  = master_test2,
                service = service
        )
        review1 = Review.objects.create(
            user    = user_test1,
            master  = master_test1,
            service = service,
            rating  = 4.5,
        )
        review2 = Review.objects.create(
            user    = user_test2,
            master  = master_test1,
            service = service,
            rating  = 5.0,
        ) 

    def test_service_details_response_success(self):
        user=User.objects.get(id=1)
        AVG_RATING = (4.5+5.0)/2
        service1   = Service.objects.get(id=1)
        user_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM)
        headers    = {"HTTP_Authorization" : user_token}
        
        response = client.get('/services/details',{'serviceId': 1}, **headers, content_type='application/json')
        self.assertEqual(
            response.json(),{
                                "MESSAGE": "SUCCESS",
                                "DETAIL": {
                                    "name"         : service1.name,
                                    "activeMaster" : 2,
                                    "avgRating"    : str(round(AVG_RATING,1)),
                                    "totalReview"  : 2,
                                    "totalRequest" : 0
                                }
                            }
                        )

        self.assertEqual(response.status_code, 200)

    def test_service_details_response_service_does_not_exist_fail(self):
        user       = User.objects.get(id=1)
        user_token = jwt.encode({'user_id':user.id}, SECRET_KEY, algorithm=ALGORITHM)
        headers         = {"HTTP_Authorization" : user_token}
        response = client.get('/services/details',{'serviceId': 5}, **headers, content_type='application/json')
        self.assertEqual(response.json(),
            {
                "MESSAGE": "SERVICE_DOES_NOT_EXISTS"
            }
        )
        self.assertEqual(response.status_code, 404)

    def test_service_details_user_not_loggedin(self):
        response = client.get('/services/details',{'serviceId': 5}, content_type='application/json')
        self.assertEqual(response.json(),
            {
                "MESSAGE": "LOGIN_REQUIRED"
            }
        )
        self.assertEqual(response.status_code, 401)

    def test_service_details_user_invalid(self):
        hashed_password = bcrypt.hashpw('1a2s3d4f'.encode('utf-8'), bcrypt.gensalt())
        user            = 4
        user_token      = jwt.encode({'user_id':user}, SECRET_KEY, algorithm=ALGORITHM)
        headers         = {"HTTP_Authorization" : user_token}
        response        = client.get('/services/details',{'serviceId': 1}, **headers, content_type='application/json')
        self.assertEqual(response.json(),
            {
               "MESSAGE": "INVALID_USER"
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_service_details_token_JWT_decode_error(self):
        user       = User.objects.get(id=1)
        SECRET     = 'FAKE_SECRET'
        user_token = jwt.encode({'user_id':user.id}, SECRET, algorithm=ALGORITHM)
        headers    = {"HTTP_Authorization" : user_token}
        response   = client.get('/services/details',{'serviceId': 1}, **headers, content_type='application/json')
        self.assertEqual(response.json(),
            {
               "MESSAGE": "JWT_DECODE_ERROR"
            }
        )
        self.assertEqual(response.status_code, 400)

class RegionViewTest(TransactionTestCase):
    reset_sequences = True
    def setUp(self):
        region1 = Region.objects.create(name='region1')
        region2 = Region.objects.create(name='region2')
        SubRegion.objects.create(region=region1,name='test1')
        SubRegion.objects.create(region=region1,name='test2')
        SubRegion.objects.create(region=region2,name='test3')
        SubRegion.objects.create(region=region2,name='test4')

    def test_regions_list_response_success(self):
        response = client.get('/services/regions', HTTP_ACCEPT='application/json')
        self.assertEqual(response.json(),
            {
                "Regions": [
                    {
                        "name": "region1",
                        "subregions": [
                            "test1",
                            "test2",
                        ]
                    },
                    {
                        "name": "region2",
                        "subregions": [
                            "test3",
                            "test4",
                        ]
                    },
                ]
            }
        )

        self.assertEqual(response.status_code, 200)