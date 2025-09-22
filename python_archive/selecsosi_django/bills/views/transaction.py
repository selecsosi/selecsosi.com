from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import ListView, DetailView

from ..models import Transaction


class TransactionListView(ListView):
    queryset = Transaction.objects.all()
    template_name = "bill/transaction/transaction_list.html"


class TransactionDetailView(DetailView):
    model = Transaction
    template_name = "bill/transaction/transaction_detail.html"
    slug_url_kwarg = "id"
    slug_field = "id"
    context_object_name = "transaction"
