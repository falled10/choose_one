from django.urls import path

from profiles.views import ForgetPasswordView, ResetPasswordView, UserProfileView, ChangePasswordView

app_name = 'profile'

urlpatterns = [
    path('', UserProfileView.as_view(), name='profile'),
    path('password/update/', ChangePasswordView.as_view(), name='password-update'),
    path('password/forget/', ForgetPasswordView.as_view(), name='password-forget'),
    path('password/reset/', ResetPasswordView.as_view(), name='password-reset')
]
