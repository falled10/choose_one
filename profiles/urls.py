from django.urls import path

from profiles.views import UserProfileView


app_name = 'profiles'

urlpatterns = [
    path('', UserProfileView.as_view(), name='profile')
]
