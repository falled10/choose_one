from django.db import models

from authentication.models import User
from polls.choices import MediaType


class Poll(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='polls')
    title = models.CharField(max_length=255)
    places_number = models.PositiveIntegerField()
    media_type = models.CharField(choices=MediaType.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'polls'
        verbose_name = 'Poll'
        verbose_name_plural = 'Polls'


class Option(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='options')
    label = models.CharField(max_length=255)
    media = models.FileField()
