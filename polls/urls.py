from rest_framework.routers import SimpleRouter
from rest_framework_nested import routers

from polls.views import PollViewSet, OptionViewSet


app_name = 'polls'

router = SimpleRouter()

router.register('', PollViewSet, basename='polls')

option_router = routers.NestedSimpleRouter(router, '', lookup='poll')
option_router.register('options', OptionViewSet, basename='poll-options')

urlpatterns = [

] + router.urls + option_router.urls
