from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, \
    DestroyModelMixin

from choose_one.paginators import ResultSetPagination
from polls.serializers import PollSerializer, OptionSerializer
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

    @action(methods=['POST'], detail=True, url_name='add-option', url_path='add-option',
            serializer_class=OptionSerializer)
    def add_option(self, request, slug=None, *args, **kwargs):
        poll = get_object_or_404(Poll, slug=slug, creator=self.request.user)
        serializer = self.get_serializer_class()(data=request.data, context={'poll': poll})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED, data=serializer.data)
