from django.db import models
from django.utils.text import slugify

from authentication.models import User
from polls.choices import MediaType
from static_content.utils import upload_to


class Poll(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polls')
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=255, unique=True)
    places_number = models.PositiveIntegerField()
    media_type = models.CharField(choices=MediaType.choices, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'polls'
        verbose_name = 'Poll'
        verbose_name_plural = 'Polls'

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    label = models.CharField(max_length=255)
    media = models.FileField(upload_to=upload_to)

    class Meta:
        db_table = 'options'
        verbose_name = 'Option'
        verbose_name_plural = 'Options'
