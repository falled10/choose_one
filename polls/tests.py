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
        self.poll = mixer.blend(Poll, creator=self.user, places_number=2)
        self.option = mixer.blend(Option, poll=self.poll)
        self.data = {
            'title': 'some-new-poll',
            'places_number': 2,
            'media_type': 'IMAGE',
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

    def test_create_new_poll_odd_places_number(self):
        data = self.data.copy()
        data['places_number'] = 3
        resp = self.client.post(reverse('polls:polls-list'), data=data)
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

    def test_add_new_option_to_poll(self):
        image_name = 'test_image.png'
        with open(os.path.join(settings.BASE_DIR, 'static_content/testdata/image.jpg'), 'rb') as f:
            storage_file = default_storage.open(image_name, 'wb+')
            storage_file.write(f.read())
            storage_file.close()
        option = {
            'label': 'some-new-option',
            'media': {'name': image_name}
        }
        resp = self.client.post(reverse('polls:polls-add-option', args=(self.poll.slug,)), data=option)
        default_storage.delete(image_name)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['label'], option['label'])
        self.poll.refresh_from_db()
        self.assertEqual(self.poll.options.count(), 2)

    def test_add_too_many_options_to_poll(self):
        image_name = 'test_image.png'
        with open(os.path.join(settings.BASE_DIR, 'static_content/testdata/image.jpg'), 'rb') as f:
            storage_file = default_storage.open(image_name, 'wb+')
            storage_file.write(f.read())
            storage_file.close()
        option1 = {
            'label': 'some-new-option',
            'media': {'name': image_name}
        }
        option2 = {
            'label': 'some-other-option',
            'media': {'name': image_name}
        }
        self.client.post(reverse('polls:polls-add-option', args=(self.poll.slug,)), data=option1)
        resp = self.client.post(reverse('polls:polls-add-option', args=(self.poll.slug,)), data=option2)
        default_storage.delete(image_name)
        self.assertEqual(resp.status_code, 400)
        self.poll.refresh_from_db()
        self.assertEqual(self.poll.options.count(), 2)

    def test_add_new_option_to_poll_from_another_user(self):
        another_user = self.create(email='other@mail.com', username='another-user')
        self.poll.creator = another_user
        self.poll.save()
        image_name = 'test_image.png'
        with open(os.path.join(settings.BASE_DIR, 'static_content/testdata/image.jpg'), 'rb') as f:
            storage_file = default_storage.open(image_name, 'wb+')
            storage_file.write(f.read())
            storage_file.close()
        option = {
            'label': 'some-new-option',
            'media': {'name': image_name}
        }
        resp = self.client.post(reverse('polls:polls-add-option', args=(self.poll.slug,)), data=option)
        default_storage.delete(image_name)
        self.assertEqual(resp.status_code, 404)

    def test_add_new_option_when_logout(self):
        self.logout()
        image_name = 'test_image.png'
        with open(os.path.join(settings.BASE_DIR, 'static_content/testdata/image.jpg'), 'rb') as f:
            storage_file = default_storage.open(image_name, 'wb+')
            storage_file.write(f.read())
            storage_file.close()
        option = {
            'label': 'some-new-option',
            'media': {'name': image_name}
        }
        resp = self.client.post(reverse('polls:polls-add-option', args=(self.poll.slug,)), data=option)
        default_storage.delete(image_name)
        self.assertEqual(resp.status_code, 401)

    def test_add_new_option_for_non_existed_poll(self):
        image_name = 'test_image.png'
        with open(os.path.join(settings.BASE_DIR, 'static_content/testdata/image.jpg'), 'rb') as f:
            storage_file = default_storage.open(image_name, 'wb+')
            storage_file.write(f.read())
            storage_file.close()
        option = {
            'label': 'some-new-option',
            'media': {'name': image_name}
        }
        resp = self.client.post(reverse('polls:polls-add-option', args=('some-non-existed-poll',)), data=option)
        default_storage.delete(image_name)
        self.assertEqual(resp.status_code, 404)
