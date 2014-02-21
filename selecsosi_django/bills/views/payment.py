import decimal
from decimal import *

from django.db import transaction
from django.http import HttpResponseRedirect  # , HttpResponse
from django.shortcuts import render_to_response
from django.core.urlresolvers import reverse
# from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required

from ..models import Account, Bill, BillParticipant, Transaction, Group



# def get_account_id(request):
#     account_id = request.session.get("account_id", None)
#     if not account_id:
#         user = request.user
#         user_account = Account.objects.get(user__id=user.id)
#         account_id = user_account.id
#         request.session["account_id"] = account_id
#     return account_id
#
#
# @login_required
# def create(request):
#     account_id = get_account_id(request)
#     if request.method == "POST":
#         pass
#     elif request.method == "GET":
#         accounts = [x.to_account for x in Transaction.objects.filter(from_account_id=account_id, amount_remaining__gt=Decimal(0))]
#         d = {
#             "to_account": {
#                 "choices": [(x.id, x.user.username) for x in accounts],
#             }
#         }
#         form = ChoseToAccountForm(initial=d)
#
#     return render_to_response("bills/payment/create.html",
#         {
#             "form": form,
#         },
#         context_instance=RequestContext(request))
