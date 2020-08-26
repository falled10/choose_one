from django.conf import settings
from rest_framework.parsers import FileUploadParser

from static_content.utils import filename_generator


class ImageUploadParser(FileUploadParser):
    media_type = 'image/*'

    def get_filename(self, stream, media_type, parser_context):
        ext = settings.IMAGE_DEFAULT_EXTENSION
        return f"{filename_generator()}.{ext}"
