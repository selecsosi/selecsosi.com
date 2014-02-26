from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models import Q

from ..models import Account, Group, Transaction


@login_required
def index(request):
    return HttpResponseRedirect("/bills/dashboard/")


@login_required
def dashboard(request):
    account = Account.objects.get(user=request.user)
    groups = Group.objects.filter(accounts=account)
    transactions = Transaction.objects.filter(Q(to_account=account) | Q(from_account=account))
    d = {
        'groups': groups,
        'transactions': transactions,
    }
    return render_to_response('../templates/dashboard.html',
        d,
        context_instance=RequestContext(request))
