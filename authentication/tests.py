from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from authentication.models import User
from choose_one.tests import BaseAPITest


class APITestObtainJSONWebToken(BaseAPITest):

    def setUp(self):
        self.email = "test@mail.com"
        self.password = "test_password"
        self.user = self.create(email=self.email, password=self.password)

    def test_get_token_pair(self):
        resp = self.client.post(reverse('authentication:auth'), data={'email': self.email, 'password': self.password})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('refresh', resp.data)
        self.assertIn('access', resp.data)

    def test_get_token_authentication_error(self):
        resp = self.client.post(reverse('authentication:auth'), data={'email': 'fake_data', 'password': 'fake_data'})
        self.assertEqual(resp.status_code, 401)


class APITestVerifyJSONWebToken(BaseAPITest):

    def setUp(self):
        self.email = "test@mail.com"
        self.password = "test_password"
        self.user = self.create(email=self.email, password=self.password)
        self.access_token = str(AccessToken.for_user(self.user))

    def test_token_is_valid(self):
        resp = self.client.post(reverse('authentication:auth-verify'), data={'token': self.access_token})
        self.assertEqual(resp.status_code, 200)

    def test_get_token_validation_error(self):
        resp = self.client.post(reverse('authentication:auth-verify'), data={'token': 'fake_data'})
        self.assertEqual(resp.status_code, 401)


class APITestRefreshJSONWebToken(BaseAPITest):

    def setUp(self):
        self.email = "test@mail.com"
        self.password = "test_password"
        self.user = self.create(email=self.email, password=self.password)
        self.refresh_token = str(RefreshToken.for_user(self.user))

    def test_get_access_token(self):
        resp = self.client.post(reverse('authentication:auth-refresh'), data={'refresh': self.refresh_token})
        self.assertIn('access', resp.data)

    def test_get_token_refresh_error(self):
        resp = self.client.post(reverse('authentication:auth-refresh'), data={'refresh': 'fake_data'})
        self.assertEqual(resp.status_code, 401)


class TestSignUpView(BaseAPITest):

    def test_register_new_user(self):
        data = {
            'email': 'test@mail.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        resp = self.client.post(reverse('authentication:auth-register'), data=data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(User.objects.count(), 1)

    def test_register_with_invalid_data(self):
        data = {
            'email': 'something',
            'username': '',
            'password': 'testpass123'
        }
        resp = self.client.post(reverse('authentication:auth-register'), data=data)
        self.assertEqual(resp.status_code, 400)

    def test_register_user_with_already_existed_email(self):
        user = self.create_and_login()
        data = {
            'email': user.email,
            'username': 'testuser',
            'password': 'testpass123'
        }
        resp = self.client.post(reverse('authentication:auth-register'), data=data)
        self.assertEqual(resp.status_code, 400)
