from django.conf.urls import patterns, url

urlpatterns = patterns('bills.views',
    url(r'^$', 'index'),
    url(r'^dashboard/$', 'dashboard'),
    url(r'^bill/create/$', 'bill.create'),
    url(r'^bill/create/(?P<form_part>\d+)/$', 'bill.create'),
    #url(r'^payment/create/$', 'payment.create'),
    #url(r'^.*$', 'index'),
)
