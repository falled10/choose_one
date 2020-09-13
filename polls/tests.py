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
        self.data = {
            'title': 'some-new-poll',
            'media_type': 'IMAGE',
        }

    def test_get_list_of_all_polls(self):
        resp = self.client.get(reverse('polls:polls-list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['results'][0]['id'], self.poll.id)

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

    def test_create_new_poll_logout_user(self):
        self.logout()
        resp = self.client.post(reverse('polls:polls-list'), data=self.data)
        self.assertEqual(resp.status_code, 401)

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

    def test_get_my_polls(self):
        another_user = self.create(email='other@mail.com', username='another-user')
        mixer.blend(Poll, creator=another_user)
        resp = self.client.get(reverse('polls:polls-my-polls'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['count'], 1)
        self.assertEqual(resp.data['results'][0]['id'], self.poll.id)


class TestOptionViewSet(BaseAPITest):

    def setUp(self):
        self.user = self.create_and_login()
        self.poll = mixer.blend(Poll, creator=self.user)
        self.option = mixer.blend(Option, poll=self.poll)
        self.image_name = 'test_image.png'
        with open(os.path.join(settings.BASE_DIR, 'static_content/testdata/image.jpg'), 'rb') as f:
            storage_file = default_storage.open(self.image_name, 'wb+')
            storage_file.write(f.read())
            storage_file.close()

    def tearDown(self):
        default_storage.delete(self.option.media.name)
        default_storage.delete(self.image_name)

    def test_get_poll_options(self):
        resp = self.client.get(reverse('polls:poll-options-list', args=(self.poll.slug,)))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['id'], self.option.id)

    def test_get_poll_options_of_non_existed_poll(self):
        resp = self.client.get(reverse('polls:poll-options-list', args=('adsfasdfadsf',)))
        self.assertEqual(resp.status_code, 404)

    def test_get_poll_options_when_logout(self):
        self.logout()
        resp = self.client.get(reverse('polls:poll-options-list', args=(self.poll.slug,)))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data[0]['id'], self.option.id)

    def test_get_single_option_by_its_id(self):
        resp = self.client.get(reverse('polls:poll-options-detail', args=(self.poll.slug, self.option.id)))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['id'], self.option.id)

    def test_get_single_non_existed_option(self):
        resp = self.client.get(reverse('polls:poll-options-detail', args=(self.poll.slug, 123123)))
        self.assertEqual(resp.status_code, 404)

    def test_get_single_option_of_non_existed_poll(self):
        resp = self.client.get(reverse('polls:poll-options-detail', args=('asdfadsf', self.option.id)))
        self.assertEqual(resp.status_code, 404)

    def test_add_new_option_to_poll(self):
        option = {
            'label': 'some-new-option',
            'media': {'name': self.image_name}
        }
        resp = self.client.post(reverse('polls:poll-options-list', args=(self.poll.slug,)), data=option)
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['label'], option['label'])
        self.poll.refresh_from_db()
        self.assertEqual(self.poll.options.count(), 2)

    def test_add_new_option_to_poll_from_another_user(self):
        another_user = self.create(email='other@mail.com', username='another-user')
        self.poll.creator = another_user
        self.poll.save()
        option = {
            'label': 'some-new-option',
            'media': {'name': self.image_name}
        }
        resp = self.client.post(reverse('polls:poll-options-list', args=(self.poll.slug,)), data=option)
        self.assertEqual(resp.status_code, 400)

    def test_add_new_option_when_logout(self):
        self.logout()
        option = {
            'label': 'some-new-option',
            'media': {'name': self.image_name}
        }
        resp = self.client.post(reverse('polls:poll-options-list', args=(self.poll.slug,)), data=option)
        self.assertEqual(resp.status_code, 401)

    def test_add_new_option_for_non_existed_poll(self):
        option = {
            'label': 'some-new-option',
            'media': {'name': self.image_name}
        }
        resp = self.client.post(reverse('polls:poll-options-list', args=('some-non-existed-poll',)), data=option)
        self.assertEqual(resp.status_code, 404)

    def test_remove_one_option(self):
        resp = self.client.delete(reverse('polls:poll-options-detail', args=(self.poll.slug, self.option.id,)))
        self.assertEqual(resp.status_code, 204)
        self.poll.refresh_from_db()
        self.assertEqual(self.poll.options.count(), 0)

    def test_remove_one_option_non_existed_poll(self):
        resp = self.client.delete(reverse('polls:poll-options-detail', args=('asdfadsfasdf', self.option.id,)))
        self.assertEqual(resp.status_code, 404)

    def test_remove_one_non_existed_option(self):
        resp = self.client.delete(reverse('polls:poll-options-detail', args=(self.poll.slug, 123123,)))
        self.assertEqual(resp.status_code, 404)

    def test_update_single_option(self):
        data = {
            'label': 'some-new-label',
            'media': {'name': self.image_name}
        }
        resp = self.client.put(reverse('polls:poll-options-detail', args=(self.poll.slug, self.option.id,)), data=data)
        self.assertEqual(resp.status_code, 200)
        self.option.refresh_from_db()
        self.assertEqual(self.option.label, data['label'])
        self.assertEqual(self.option.media.name, data['media']['name'])

    def test_update_single_option_invalid_data(self):
        data = {
            'label': '',
            'media': {'name': self.image_name}
        }
        resp = self.client.put(reverse('polls:poll-options-detail', args=(self.poll.slug, self.option.id,)), data=data)
        self.assertEqual(resp.status_code, 400)

    def test_update_non_existed_option(self):
        data = {
            'label': 'some-new-label',
            'media': {'name': self.image_name}
        }
        resp = self.client.put(reverse('polls:poll-options-detail', args=(self.poll.slug, 123123,)), data=data)
        self.assertEqual(resp.status_code, 404)

    def test_partial_update_single_option(self):
        data = {
            'label': 'some-new-label'
        }
        resp = self.client.patch(reverse('polls:poll-options-detail', args=(self.poll.slug, self.option.id,)),
                                 data=data)
        self.assertEqual(resp.status_code, 200)
        self.option.refresh_from_db()
        self.assertEqual(self.option.label, data['label'])
