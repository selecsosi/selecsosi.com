from decimal import Decimal
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.db.models import Q
from django.db.models import Sum

from ..models import Account, Group, Transaction


@login_required
def index(request):
    return HttpResponseRedirect("/bills/dashboard/")


@login_required
def dashboard(request):
    account = Account.objects.get(user=request.user)
    groups = Group.objects.filter(accounts=account)
    transactions = Transaction.objects.filter(Q(to_account=account) | Q(from_account=account))[:10 ]
    debits = Transaction.objects.filter(Q(from_account=account) & Q(transfer_type="D")).aggregate(Sum('amount'))
    credit = Transaction.objects.filter(Q(to_account=account) & Q(transfer_type="C")).aggregate(Sum('amount'))
    owed = Transaction.objects.filter(Q(to_account=account) & Q(transfer_type="D")).aggregate(Sum('amount'))
    if debits["amount__sum"] is not None:
        debits = debits["amount__sum"]
    else:
        debits = Decimal("0.00")
    if credit["amount__sum"] is not None:
        credit = credit["amount__sum"]
    else:
        credit = Decimal("0.00")
    if owed["amount__sum"] is not None:
        owed = owed["amount__sum"]
    else:
        owed = Decimal("0.00")
    d = {
        'owed': owed,
        'balance': credit - debits,
        'groups': groups,
        'transactions': transactions,
    }
    return render_to_response('bill/dashboard.html',
        d,
        context_instance=RequestContext(request))
