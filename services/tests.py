from django.test     import TestCase, Client, TransactionTestCase
from unittest.mock   import patch, MagicMock
from services.models import Category, Service

import json

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
                        'category_id'     :1,
                        'name'           :'Test1',
                        'icon_image_url' :'test_icon.url1',              
                    },
                    {
                        'category_id'     :2,
                        'name'           :'Test2',
                        'icon_image_url' :'test_icon.url2',              
                    },
                    {
                        'category_id'     :3,
                        'name'           :'Test3',
                        'icon_image_url' :'test_icon.url3',              
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
            category = cat_id,
            name = 'test1',
            image_url = 'test.url1',
        )
        Service.objects.create(
            category = cat_id,
            name = 'test2',
            image_url = 'test.url2'
        )

    def tearDown(self):
        Category.objects.all().delete()
        Service.objects.all().delete()

    def test_servicelist1_response_success(self):
        reset_squences = True
        response = client.get('/services/services',{'catCd': 1}, HTTP_ACCEPT='application/json')
        self.assertEqual(
            response.json(),{ 
                "Category": "Test",
                "RESULT": [
                    {
                        'service_id' :1,
                        'name'       :'test1',
                        'image_url'  :'test.url1',              
                    },
                    {
                        'service_id' :2,
                        'name'       :'test2',
                        'image_url'  :'test.url2',              
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