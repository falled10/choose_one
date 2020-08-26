from django.db import transaction
from rest_framework import serializers

from static_content.serializers import ModelFileSerializer, FileUploadSerializer
from polls.models import Poll, Option


class OptionSerializer(ModelFileSerializer):
    media = FileUploadSerializer()

    class Meta:
        model = Option
        fields = ('id', 'poll', 'label', 'media')
        read_only_fields = ('id', 'poll')


class PollSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = Poll
        fields = ('id', 'title', 'places_number', 'media_type', 'options')

    def validate_places_number(self, value):
        if value <= 0 or value % 2 != 0:
            raise serializers.ValidationError('Places should be even number')
        return value

    def validate(self, data):
        if len(data['options']) != data['places_number']:
            raise serializers.ValidationError('Number of options should be equal to number of places')
        return super().validate(data)

    @transaction.atomic
    def create(self, validated_data):
        user = self.context['request'].user
        options = validated_data.pop('options')
        poll = Poll.objects.create(**validated_data, creator=user)

        for option in options:
            media = option.pop('media')
            Option.objects.create(**option, media=media['name'], poll=poll)

        return poll
