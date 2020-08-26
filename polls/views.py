from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, \
    DestroyModelMixin

from choose_one.paginators import ResultSetPagination
from polls.serializers import PollSerializer
from polls.models import Poll
from polls.permissions import IsAuthenticatedOrReadOnly


class PollViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, DestroyModelMixin):
    """
    list:
    Returns list of all available polls

    Returns list of all available polls

    retrieve:
    Returns single poll by its slug

    Returns single poll by its slug

    create:
    Create new poll

    Create new poll

    destroy:
    Remove poll by its slug

    Remove poll by its slug, user should be creator of this poll
    """
    serializer_class = PollSerializer
    lookup_field = 'slug'
    pagination_class = ResultSetPagination
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        if self.action == 'destroy':
            return Poll.objects.filter(creator=self.request.user)
        return Poll.objects.all()
