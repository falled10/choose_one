from rest_framework.generics import get_object_or_404
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from choose_one.paginators import ResultSetPagination
from polls.permissions import IsOwnerOrReadOnly
from polls.serializers import PollSerializer, OptionSerializer
from polls.models import Poll, Option


class PollViewSet(ModelViewSet):
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

    my_polls:
    Return user's polls

    Return user's polls
    """
    serializer_class = PollSerializer
    lookup_field = 'slug'
    pagination_class = ResultSetPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly)
    queryset = Poll.objects.all()

    @action(detail=False, methods=['GET'], url_path='my-polls', url_name='my-polls',
            permission_classes=(IsAuthenticated,))
    def my_polls(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(creator=self.request.user)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class OptionViewSet(ModelViewSet):
    """
    list:
    Return list of options

    Return list of poll's options

    retrieve:
    Return single option

    Return single poll's option

    create:
    Create new option

    Create new poll's option

    destroy:
    Remove single option

    Remove single poll's option

    update:
    Update single option

    Update single poll's option

    partial_update:
    Partial Update single option

    Partial Update single poll's option
    """
    serializer_class = OptionSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return Option.objects.filter(poll__slug=self.kwargs['poll_slug'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        poll = get_object_or_404(Poll, slug=self.kwargs['poll_slug'])
        context['poll'] = poll
        return context
