from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import serializers

from authentication.models import User
from authentication.tokens import TokenGenerator
from choose_one.tasks import send_email


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        if not User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError('User with this email does not exist.')
        return data

    def send_by_email(self):
        user = User.objects.get(email=self.data['email'])
        token = f"{urlsafe_base64_encode(force_bytes(user.email))}.{TokenGenerator.make_token(user)}"
        url = f"{settings.PASSWORD_RESET_URL}?token={token}"
        send_email.delay(
            subject="ChooseOne Password Restoring",
            template='notifications/password_forget.html',
            recipients=[user.email],
            context={'url': url, 'email': user.email}
        )


class PasswordSerializer(serializers.Serializer):
    """
    Base serializer for password changing
    """
    new_password = serializers.CharField(required=True)
    confirmed_password = serializers.CharField(required=True)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        data = super().validate(attrs)
        new_password = data['new_password']
        confirmed_password = data['confirmed_password']
        if new_password != confirmed_password:
            raise serializers.ValidationError("The two password fields didn't match.")
        return data


class ChangePasswordSerializer(PasswordSerializer):

    def update(self, instance, validated_data):
        self.instance.set_password(validated_data['new_password'])
        self.instance.save()
        return self.instance


class PasswordResetSerializer(PasswordSerializer):
    token = serializers.CharField(required=True)

    def validate_token(self, value):
        try:
            email_b64, token = value.split('.')
            self.user = User.objects.get(email=urlsafe_base64_decode(email_b64).decode('utf-8'))
        except ValueError:
            raise serializers.ValidationError("Email is not valid base64 string")
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")
        if not TokenGenerator.check_token(self.user, token):
            raise serializers.ValidationError("Token is invalid or expired")
        return value

    def create(self, validated_data):
        self.user.set_password(validated_data['new_password'])
        self.user.save()
        return self.user
