import unittest, json, jwt
import bcrypt

from django.test  import TestCase,Client

from .models import User,Gender


class UserSignUpSignInTest(unittest.TestCase):
    
    def setUp(self):
        hashed_password = bcrypt.hashpw('1a2s3d4f'.encode('utf-8'), bcrypt.gensalt())
        User.objects.create(
            name     = '장장장',
            email    = 'jun1714@mail.com',
            password = hashed_password.decode()
        )
    
    def tearDown(self):
        User.objects.all().delete()

    def test_user_post_signup_success(self):
        client = Client()
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
        client = Client()
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
        client = Client()
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
        client = Client()
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
        client = Client()
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
        client = Client()
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
        client = Client()
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