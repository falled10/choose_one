import os

from django.core.files.storage import default_storage
from django.urls import reverse
from django.conf import settings
from PIL import Image

from choose_one.tests import BaseAPITest


class APITestImageUpload(BaseAPITest):

    def setUp(self):
        self.create_and_login()

    def test_send_image_binary(self):
        with open(os.path.join(settings.BASE_DIR, 'static_content/testdata/image.jpg'), 'rb') as f:
            file = f.read()
        resp = self.client.post(reverse('static_content:image-upload'), content_type='image/jpeg',
                                data=file)

        file_exists = default_storage.exists(resp.data['name'])
        default_storage.delete(resp.data['name'])
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(file_exists)
        self.assertIsNotNone(resp.data['name'])
        self.assertIsNotNone(resp.data['url'])

    def test_send_wrong_data(self):
        with open(os.path.join(settings.BASE_DIR, 'static_content/testdata/not_image.jpg'), 'rb') as f:
            file = f.read()
        resp = self.client.post(reverse('static_content:image-upload'), content_type='image/jpeg',
                                data=file)
        self.assertEqual(resp.status_code, 400)

    def test_upload_image_with_resize(self):
        with open(os.path.join(settings.BASE_DIR, 'static_content/testdata/image.jpg'), 'rb') as f:
            file = f.read()
        resp = self.client.post(reverse('static_content:image-upload'), content_type='image/jpeg',
                                data=file)
        self.assertEqual(resp.status_code, 201)

        with default_storage.open(resp.data['name']) as f:
            im = Image.open(f)
            w, h = im.size
            self.assertLessEqual(w, settings.IMAGE_MAX_WIDTH)
        default_storage.delete(resp.data['name'])
