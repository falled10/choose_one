import os

from mixer.backend.django import mixer
from django.urls import reverse
from django.core.files.storage import default_storage
from django.conf import settings

from choose_one.tests import BaseAPITest
from polls.models import Poll, Option


class TestPollViewSet(BaseAPITest):

    def setUp(self):
        self.user = self.create_and_login()
        self.poll = mixer.blend(Poll, creator=self.user)
        self.option = mixer.blend(Option, poll=self.poll)
        self.data = {
            'title': 'some-new-poll',
            'places_number': 2,
            'media_type': 'IMAGE',
            'options': []
        }

    def tearDown(self):
        default_storage.delete(self.option.media.name)

    def test_get_list_of_all_polls(self):
        resp = self.client.get(reverse('polls:polls-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['results'][0]['id'], self.poll.id)
        self.assertEqual(resp.data['results'][0]['options'][0]['id'], self.option.id)

    def test_get_list_of_all_polls_when_logout(self):
        self.logout()
        resp = self.client.get(reverse('polls:polls-list'))
        self.assertEqual(resp.status_code, 200)

    def test_get_single_poll(self):
        resp = self.client.get(reverse('polls:polls-detail', args=(self.poll.slug,)))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['id'], self.poll.id)

    def test_get_single_poll_logout(self):
        self.logout()
        resp = self.client.get(reverse('polls:polls-detail', args=(self.poll.slug,)))
        self.assertEqual(resp.status_code, 200)

    def test_get_single_poll_from_another_user(self):
        another_user = self.create(email='other@mail.com', username='another-user')
        self.poll.creator = another_user
        self.poll.save()
        resp = self.client.get(reverse('polls:polls-detail', args=(self.poll.slug,)))
        self.assertEqual(resp.status_code, 200)

    def test_get_single_poll_404(self):
        resp = self.client.get(reverse('polls:polls-detail', args=('something',)))
        self.assertEqual(resp.status_code, 404)

    def test_create_new_poll(self):
        data = self.data.copy()
        image_name = 'test_image.png'
        with open(os.path.join(settings.BASE_DIR, 'static_content/testdata/image.jpg'), 'rb') as f:
            storage_file = default_storage.open(image_name, 'wb+')
            storage_file.write(f.read())
            storage_file.close()
        data['options'].append({
            'label': 'some-new-option',
            'media': {'name': image_name}
        })
        data['options'].append({
            'label': 'some-another-option',
            'media': {'name': image_name}
        })
        resp = self.client.post(reverse('polls:polls-list'), data=data)
        default_storage.delete(image_name)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['title'], data['title'])
        self.assertEqual(resp.data['options'][0]['label'], data['options'][0]['label'])
        self.assertEqual(resp.data['options'][0]['media']['name'], image_name)

    def test_create_new_poll_odd_places_number(self):
        data = self.data.copy()
        data['places_number'] = 3
        resp = self.client.post(reverse('polls:polls-list'), data=data)
        self.assertEqual(resp.status_code, 400)

    def test_create_new_poll_options_count_not_equal_to_places_number(self):
        data = self.data.copy()
        image_name = 'something'
        with open(os.path.join(settings.BASE_DIR, 'static_content/testdata/image.jpg'), 'rb') as f:
            storage_file = default_storage.open(image_name, 'wb+')
            storage_file.write(f.read())
            storage_file.close()
        data['options'].append({
            'label': 'some-new-option',
            'media': {'name': image_name}
        })
        resp = self.client.post(reverse('polls:polls-list'), data=data)
        default_storage.delete(image_name)
        self.assertEqual(resp.status_code, 400)

    def test_create_new_poll_logout_user(self):
        self.logout()
        resp = self.client.post(reverse('polls:polls-list'), data=self.data)
        self.assertEqual(resp.status_code, 401)

    def test_create_new_poll_places_number_is_zero(self):
        data = self.data.copy()
        data['places_number'] = 0
        resp = self.client.post(reverse('polls:polls-list'), data=data)
        self.assertEqual(resp.status_code, 400)

    def test_remove_poll(self):
        resp = self.client.delete(reverse('polls:polls-detail', args=(self.poll.slug,)))
        self.assertEqual(resp.status_code, 204)
        self.assertEqual(Poll.objects.count(), 0)

    def test_remove_poll_of_another_user(self):
        another_user = self.create(email='other@mail.com', username='another-user')
        self.poll.creator = another_user
        self.poll.save()
        resp = self.client.delete(reverse('polls:polls-detail', args=(self.poll.slug,)))
        self.assertEqual(resp.status_code, 404)

    def test_remove_poll_logout_user(self):
        self.logout()
        resp = self.client.delete(reverse('polls:polls-detail', args=(self.poll.slug,)))
        self.assertEqual(resp.status_code, 401)

    def test_remove_poll_404(self):
        resp = self.client.delete(reverse('polls:polls-detail', args=('something',)))
        self.assertEqual(resp.status_code, 404)
