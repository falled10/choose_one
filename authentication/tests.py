from unittest.mock import patch

from django.urls import reverse
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from authentication.models import User
from authentication.tokens import TokenGenerator
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

    @patch('choose_one.tasks.send_email.delay')
    def test_register_new_user(self, send):
        data = {
            'email': 'test@mail.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        resp = self.client.post(reverse('authentication:auth-register'), data=data)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(User.objects.count(), 1)
        send.assert_called_once()

    @patch('choose_one.tasks.send_email.delay')
    def test_register_with_invalid_data(self, send):
        data = {
            'email': 'something',
            'username': '',
            'password': 'testpass123'
        }
        resp = self.client.post(reverse('authentication:auth-register'), data=data)
        self.assertEqual(resp.status_code, 400)
        send.assert_not_called()

    @patch('choose_one.tasks.send_email.delay')
    def test_register_user_with_already_existed_email(self, send):
        user = self.create_and_login()
        data = {
            'email': user.email,
            'username': 'testuser',
            'password': 'testpass123'
        }
        resp = self.client.post(reverse('authentication:auth-register'), data=data)
        self.assertEqual(resp.status_code, 400)
        send.assert_not_called()


class TestUserActivation(BaseAPITest):
    def setUp(self):
        self.user = self.create()
        self.user.is_active = False
        self.user.save()

    def test_user_activation(self):
        token = f"{urlsafe_base64_encode(force_bytes(self.user.email))}.{TokenGenerator.make_token(self.user)}"
        resp = self.client.post(reverse('authentication:auth-activate'), data={'token': token})
        self.user.refresh_from_db()
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(self.user.is_active)

    def test_user_activation_returns_access_token(self):
        token = f"{urlsafe_base64_encode(force_bytes(self.user.email))}.{TokenGenerator.make_token(self.user)}"
        resp = self.client.post(reverse('authentication:auth-activate'), data={'token': token})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('access_token' in resp.data.keys())
        self.assertTrue('refresh_token' in resp.data.keys())

    def test_user_activation_wrong_uid(self):
        token = f"something.{TokenGenerator.make_token(self.user)}"
        resp = self.client.post(reverse('authentication:auth-activate'), data={'token': token})
        self.assertEqual(resp.status_code, 400)

    def test_user_activation_wrong_token(self):
        token = f"{urlsafe_base64_encode(force_bytes(self.user.email))}.something"
        resp = self.client.post(reverse('authentication:auth-activate'), data={'token': token})
        self.assertEqual(resp.status_code, 400)
