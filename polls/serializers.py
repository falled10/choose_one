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
        poll = self.context['poll']
        if poll.places_number == poll.options.count() and not self.instance:
            raise serializers.ValidationError('Number of options should be equal to number of places')
        return attrs

    def create(self, validated_data):
        poll = self.context['poll']
        media = validated_data.pop('media')
        option = Option.objects.create(**validated_data, media=media['name'], poll=poll)
        return option


class PollSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = Poll
        fields = ('id', 'title', 'places_number', 'media_type', 'options')

    def validate_places_number(self, value):
        if value <= 0 or value % 2 != 0:
            raise serializers.ValidationError('Places should be even number')
        return value

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        poll = Poll.objects.create(**validated_data, creator=user)
        return poll
