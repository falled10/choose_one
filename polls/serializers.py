from django.db import transaction
from rest_framework import serializers

from static_content.serializers import ModelFileSerializer, FileUploadSerializer
from polls.models import Poll, Option


class OptionSerializer(ModelFileSerializer):
    media = FileUploadSerializer()

    class Meta:
        model = Option
        fields = ('id', 'label', 'media')
        read_only_fields = ('id',)

    def validate(self, attrs):
        user = self.context['request'].user
        poll = self.context['poll']
        if user != poll.creator:
            raise serializers.ValidationError("You cannot add option to other user's poll")
        return attrs

    def create(self, validated_data):
        poll = self.context['poll']
        media = validated_data.pop('media')
        option = Option.objects.create(**validated_data, media=media['name'], poll=poll)
        return option

    def update(self, instance, validated_data):
        media = validated_data.pop('media', None)
        if media:
            validated_data['media'] = media['name']
        return super().update(instance, validated_data)


class PollSerializer(ModelFileSerializer):
    image = FileUploadSerializer(read_only=True)

    class Meta:
        model = Poll
        fields = ('id', 'title', 'media_type', 'description', 'image', 'slug')
        read_only_fields = ('id', 'slug')

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        poll = Poll.objects.create(**validated_data, creator=user)
        return poll
