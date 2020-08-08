from django.urls import path

from authentication.views import ObtainJSONWebToken, VerifyJSONWebToken, RefreshJSONWebToken, SignUpView

app_name = 'authentication'

urlpatterns = [
    path('', ObtainJSONWebToken.as_view(), name='auth'),
    path('verify/', VerifyJSONWebToken.as_view(), name='auth-verify'),
    path('refresh/', RefreshJSONWebToken.as_view(), name='auth-refresh'),
    path('register/', SignUpView.as_view(), name='auth-register')
]