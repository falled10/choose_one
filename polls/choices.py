from django.db import models


class MediaType(models.TextChoices):
    IMAGE = 'IMAGE'
    GIF = 'GIF'
    VIDEO = 'VIDEO'
