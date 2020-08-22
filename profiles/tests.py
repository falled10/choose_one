from django.urls import reverse

from choose_one.tests import BaseAPITest


class TestUserProfile(BaseAPITest):

    def setUp(self):
        self.user = self.create_and_login()
        self.data = {
            'username': 'other-username',
            'email': 'otheremail@mail.com'
        }

    def test_get_user_profile(self):
        resp = self.client.get(reverse('profiles:profile'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['id'], self.user.id)
        self.assertEqual(resp.data['username'], self.user.username)

    def test_get_user_profile_logout_user(self):
        self.logout()
        resp = self.client.get(reverse('profiles:profile'))
        self.assertEqual(resp.status_code, 401)

    def test_update_user_profile(self):
        resp = self.client.put(reverse('profiles:profile'), data=self.data)
        self.user.refresh_from_db()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.user.username, self.data['username'])
        self.assertEqual(self.user.email, self.data['email'])

    def test_update_user_profile_wrong_data(self):
        data = {
            'username': '',
            'email': 'asdfadf'
        }
        resp = self.client.put(reverse('profiles:profile'), data=data)
        self.assertEqual(resp.status_code, 400)

    def test_update_user_profile_when_logout(self):
        self.logout()
        resp = self.client.put(reverse('profiles:profile'), data=self.data)
        self.assertEqual(resp.status_code, 401)

    def test_update_partial_user_profile(self):
        resp = self.client.patch(reverse('profiles:profile'), data={'username': self.data['username']})
        self.user.refresh_from_db()
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.user.username, self.data['username'])
        self.assertNotEqual(self.user.email, self.data['email'])
