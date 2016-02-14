from django.conf.urls import url
from . import views

app_name = 'web'
urlpatterns = [
     url(r'^ts-playground/$', views.TypeScriptView.as_view(), name='ts_playground'),
     url(r'^jsx-playground/$', views.JSXPlayground.as_view(), name='jsx_playground'),
     url(r'^$', views.IndexView.as_view(), name='index'),
]
