import uuid

from io import BytesIO

from PIL import Image
from django.core.files.storage import default_storage
from django.utils import timezone
from django.conf import settings
from rest_framework.exceptions import ValidationError


def filename_generator():
    return f'{uuid.uuid4().hex}_{round(timezone.now().timestamp() * 1000)}'


def upload_to(instance, filename):
    """Use this function in models ``upload_to`` arguments.
    This will rename image with ``filename_generator`` when image is uploaded.
    """
    ext = filename.split('.')[-1]
    return f"{filename_generator()}.{ext}"


def resize_image(image):
    """Resize image to max width and return it
    """
    try:
        im = Image.open(image)
        w, h = im.size
        if w > settings.IMAGE_MAX_WIDTH:
            new_height = h / w * settings.IMAGE_MAX_WIDTH
            im = im.resize((int(settings.IMAGE_MAX_WIDTH), int(new_height)), Image.ANTIALIAS)
    except OSError as e:
        default_storage.delete(image.name)
        raise ValidationError(f"Wrong image format. {e}")

    return im


def bytes_from_image(image, img_format='jpeg'):
    """Converts pillow image file to bytes"""
    image = image.convert('RGB')
    with BytesIO() as output:
        image.save(output, format=img_format)
        contents = output.getvalue()
    return contents
