from unittest.mock import patch

from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from authentication.models import User
from authentication.tokens import TokenGenerator
from choose_one.tests import BaseAPITest


class TestUserProfile(BaseAPITest):

    def setUp(self):
        self.user = self.create_and_login()
        self.data = {
            'username': 'other-username',
            'email': 'otheremail@mail.com'
        }

    def test_get_user_profile(self):
        resp = self.client.get(reverse('profile:profile'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['id'], self.user.id)
        self.assertEqual(resp.data['username'], self.user.username)

    def test_get_user_profile_logout_user(self):
        self.logout()
        resp = self.client.get(reverse('profile:profile'))
        self.assertEqual(resp.status_code, 401)

    def test_update_user_profile(self):
        resp = self.client.put(reverse('profile:profile'), data=self.data)
        self.user.refresh_from_db()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.user.username, self.data['username'])
        self.assertEqual(self.user.email, self.data['email'])

    def test_update_user_profile_wrong_data(self):
        data = {
            'username': '',
            'email': 'asdfadf'
        }
        resp = self.client.put(reverse('profile:profile'), data=data)
        self.assertEqual(resp.status_code, 400)

    def test_update_user_profile_when_logout(self):
        self.logout()
        resp = self.client.put(reverse('profile:profile'), data=self.data)
        self.assertEqual(resp.status_code, 401)

    def test_update_partial_user_profile(self):
        resp = self.client.patch(reverse('profile:profile'), data={'username': self.data['username']})
        self.user.refresh_from_db()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.user.username, self.data['username'])
        self.assertNotEqual(self.user.email, self.data['email'])


class ForgetPasswordViewTest(BaseAPITest):

    @patch('choose_one.tasks.send_email.delay')
    def test_send_password_forget_email(self, send):
        user = self.create()
        resp = self.client.post(reverse('profile:password-forget'), data={"email": user.email})
        self.assertEqual(resp.status_code, 204)
        send.assert_called_once()

    @patch('choose_one.tasks.send_email.delay')
    def test_send_password_forget_email_with_invalid_email(self, send):
        resp = self.client.post(reverse('profile:password-forget'), data={"email": "some_user@mail.com"})
        self.assertEqual(resp.status_code, 400)
        send.assert_not_called()


class PasswordResetViewTest(BaseAPITest):

    def setUp(self):
        self.user = self.create_and_login()
        self.data = {
            'token': f"{urlsafe_base64_encode(force_bytes(self.user.email))}.{TokenGenerator.make_token(self.user)}",
            'new_password': 'test123password',
            'confirmed_password': 'test123password'
        }

    def test_reset_password(self):
        resp = self.client.post(reverse('profile:password-reset'), data=self.data)
        self.assertEqual(resp.status_code, 204)
        user = User.objects.get(id=self.user.id)
        self.assertTrue(user.check_password(self.data['new_password']))

    def test_reset_password_invalid_token(self):
        data_copy = self.data.copy()
        data_copy['token'] += 'something'
        resp = self.client.post(reverse('profile:password-reset'), data=data_copy)
        self.assertEqual(resp.status_code, 400)

    def test_reset_password_password_are_not_equal(self):
        data_copy = self.data.copy()
        data_copy['new_password'] += 'something'
        resp = self.client.post(reverse('profile:password-reset'), data=data_copy)
        self.assertEqual(resp.status_code, 400)

    def test_reset_password_invalid_email_in_token(self):
        data_copy = self.data.copy()
        data_copy['token'] = f"{urlsafe_base64_encode(force_bytes('123@mail.com'))}." \
                             f"{TokenGenerator.make_token(self.user)}"
        resp = self.client.post(reverse('profile:password-reset'), data=data_copy)
        self.assertEqual(resp.status_code, 400)


class ChangePasswordView(BaseAPITest):

    def setUp(self):
        self.user = self.create_and_login()
        self.data = {
            'newPassword': 'testpass123',
            'confirmedPassword': 'testpass123'
        }

    def test_change_user_password(self):
        resp = self.client.post(reverse('profile:password-update'), data=self.data)
        user = User.objects.get(pk=self.user.id)
        self.assertEqual(resp.status_code, 204)
        self.assertTrue(user.check_password(self.data['newPassword']))

    def test_change_user_password_passwords_are_not_enqual(self):
        data_copy = self.data.copy()
        data_copy['confirmedPassword'] += 'something'
        resp = self.client.post(reverse('profile:password-update'), data=data_copy)
        self.assertEqual(resp.status_code, 400)

    def test_change_user_password_when_logout(self):
        self.logout()
        resp = self.client.post(reverse('profile:password-update'), data=self.data)
        self.assertEqual(resp.status_code, 401)
