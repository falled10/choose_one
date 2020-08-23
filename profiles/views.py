from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from choose_one.schema import NO_CONTENT
from profiles.serializers import UserSerializer, ForgetPasswordSerializer, PasswordResetSerializer, \
    ChangePasswordSerializer


class UserProfileView(RetrieveUpdateAPIView):
    """
    get:
    return current user profile

    Return current user profile

    put:
    Update current user data

    Update current user data

    patch:
    update some fields in current user data

    update some fields in current user data
    """
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ForgetPasswordView(APIView):
    """
    post:
    Sends password reset notification to user email.
    ### Examples
    User should send his email like this:
    ```json
    {
        "email": "test@mail.com"
    }
    ````
    If user with this email exists, then post return status code `204`
    ### Errors
    If user sends wrong email or user with this email does not exists, then post returns status code `400`
    and response body like:
    ```json
    {
        "nonFieldErrors": [
            "User with this email does not exist."
        ]
    }
    ```
    """
    serializer_class = ForgetPasswordSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_summary="Send forget password email",
        request_body=ForgetPasswordSerializer,
        responses={204: NO_CONTENT}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.send_by_email()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ResetPasswordView(APIView):
    """
    post:
    Reset user password
    User should send new password and token that he gets from forget password link
    ### Examples
    ```json
    {
        "token": "emskdlgnkngdDFHGergergEGRerRGEgerERE346346vergd456456",
        "newPassword": "qwerty123",
        "confirmedPassword": "qwerty123"
    }
    ```
    If token is valid and passwords are equal, post returns status code `204`
    ### Errors
    If user sends invalid or expired token, post returns status code `400` and response body like:
    ```json
    {
        "token": [
            "Token is invalid or expired"
        ]
    }
    ```
    If user sends not equal passwords, post returns status code `400` and response body like:
    ```json
    {
        "nonFieldErrors": [
            "The two password fields didn't match."
        ]
    }
    ```
    """
    serializer_class = PasswordResetSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_summary="Reset user password",
        request_body=PasswordResetSerializer,
        responses={204: NO_CONTENT}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    """
    post:
    Change User password
    User should send new password to change his password
    ### Examples
    ```json
    {
        "newPassword": "qwerty123",
        "confirmedPassword": "qwerty123"
    }
    ```
    If passwords are equal, post returns status code `204`
    ### Errors
    If user sends not equal passwords, post returns status code `400` and response body like:
    ```json
    {
        "nonFieldErrors": [
            "The two password fields didn't match."
        ]
    }
    ```
    """
    serializer_class = ChangePasswordSerializer

    @swagger_auto_schema(
        operation_summary="Change user password",
        request_body=ChangePasswordSerializer,
        responses={204: NO_CONTENT}
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(instance=self.request.user, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
