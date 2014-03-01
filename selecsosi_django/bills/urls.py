from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from .views.bill.transaction import TransactionDetailView, TransactionListView
from .views.bill.groups import GroupListView, GroupDetailView

urlpatterns = patterns('bills.views',
    url(r'^$', 'home.index'),
    url(r'^dashboard/$', 'home.dashboard'),
    url(r'^bill/create/$', 'bill.create.index'),
    url(r'^bill/create/(?P<form_part>\d+)/$', 'bill.create.index'),
    url(r'^bill/start_new_bill/$', 'bill.create.start_new_bill'),
    url(r'^group/$', login_required(GroupListView.as_view()), name="groups"),
    url(r'^group/(?P<id>\d+)/$', login_required(GroupDetailView.as_view()), name="group"),
    url(r'^transaction/$', login_required(TransactionListView.as_view()), name="transactions"),
    url(r'^transaction/(?P<id>\d+)/$', login_required(TransactionDetailView.as_view()), name="transaction"),
    #url(r'^payment/create/$', 'payment.create'),
    #url(r'^.*$', 'index'),
)
