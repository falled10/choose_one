from unittest.mock import patch

from rest_framework.test import APITestCase
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone

from authentication.models import User
from choose_one.tasks import send_email


class BaseAPITest(APITestCase):

    def create(self, email='test@mail.com', username='testuser', password='qwerty123456'):
        user = User.objects.create_user(email=email, username=username, password=password)
        user.last_login_date = timezone.now()
        user.is_active = True
        user.save()

        return user

    def create_and_login(self, email='test@mail.com', username='testuser', password='qwerty123456'):
        user = self.create(email=email, username=username, password=password)
        self.authorize(user)
        return user

    def authorize(self, user, **additional_headers):
        token = AccessToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f"{api_settings.AUTH_HEADER_TYPES[0]} {token}",
            **additional_headers
        )

    def logout(self, **additional_headers):
        self.client.credentials(**additional_headers)


class TestTasks(BaseAPITest):

    def setUp(self):
        self.mail_data = {
            'subject': 'ChooseOne activate user',
            'template': 'notifications/activate_user.html',
            'context': {'url': 'http://localhost:8000/'},
            'recipients': ['test@mail.com'],
        }

    @patch('mailjet_rest.client.api_call')
    def test_send_email_task(self, send_email_task):
        def return_mock_class(*args, **kwargs):
            class MockRequest:
                status_code = 200

            return MockRequest()

        send_email_task.side_effect = return_mock_class
        send_email(**self.mail_data)
        send_email_task.assert_called_once()
