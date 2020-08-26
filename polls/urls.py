from rest_framework.routers import SimpleRouter

from polls.views import PollViewSet


app_name = 'polls'

router = SimpleRouter()

router.register('', PollViewSet, basename='polls')

urlpatterns = [

] + router.urls
