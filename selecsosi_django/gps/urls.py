from django.conf.urls import patterns, url
from .views import TripCreateView

urlpatterns = patterns('gps.views',
    url(r'^upload$', TripCreateView.as_view()),
    url(r'^$', 'index'),
)
