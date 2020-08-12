from rest_framework.generics import RetrieveUpdateAPIView

from profiles.serializers import UserSerializer


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
