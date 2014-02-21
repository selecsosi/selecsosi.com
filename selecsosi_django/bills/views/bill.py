from decimal import *

from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
# from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from ..models import Account, Bill, BillParticipant, Transaction, Group
from ..forms import ParticipationAmountForm, ParticipationFormset, StartNewBillForm, BillDetailsHeadForm, BillDetailsFootForm
from ..forms import get_choose_group_form_factory, get_choose_participants_form_factory


def get_account_id(request):
    account_id = request.session.get("account_id", None)
    if not account_id:
        user = request.user
        user_account = Account.objects.get(user__id=user.id)
        account_id = user_account.id
        request.session["account_id"] = account_id
    return account_id


def clear_bill_session(request):
    # Clear out any other bill
    for k in request.session.keys():
        if k.startswith("bill"):
            del request.session[k]


@login_required
def start_new_bill(request):
    """
    View to confirm that user wants to start a new bill
    if they happen to be in the middle of processing one
    """
    if request.method == "POST":
        form = StartNewBillForm(request.POST)
        if form.is_valid():
            start_over = form.cleaned_data["start_over"]
            if start_over:
                clear_bill_session(request)
            else:
                return HttpResponseRedirect("/bills/bill/create/%s/" % request.session["bill_form_part"])
            return HttpResponseRedirect("/bills/bill/create/1/")
    elif request.method == "GET":
        form = StartNewBillForm()
        return render_to_response(
            "bills/bill/start_new_bill.html", {
            "form": form,
            },
            context_instance=RequestContext(request))
    else:
        return HttpResponse("")


def create_1(request):
    """
    First step in the create bill process, user
    must choose a group that they are a member of
    that the bill took place between. Groups are a method
    or corralling the users bill space and only billing
    specific users that have consented
    """
    account_id = get_account_id(request)
    ChooseGroupForm = get_choose_group_form_factory(account_id)
    if request.method == "POST":
        form = ChooseGroupForm(request.POST)
        if form.is_valid():
            group_id = form.cleaned_data["group"]
            # set the group id in session to be used in the next part
            request.session["bill_group_id"] = group_id
            #update the completed form_part
            request.session["bill_form_part"] = 2
            return HttpResponseRedirect("/bills/bill/create/2/")
    elif request.method == "GET":
        form = ChooseGroupForm()
    else:
        return HttpResponse('')
    return render_to_response(
        'bills/bill/create.html', {
        'form': form,
        'request': request,
        'form_part': 1,
        },
        context_instance=RequestContext(request))


def create_2(request):
    """
    Next step is to choose the participants of the bill
    First we grab the group id from session that we got
    in create_1 to query the db and populate a participants form
    """
    group_id = request.session["bill_group_id"]
    if not group_id:
            return HttpResponseRedirect("/bills/bill/create/")

    ChooseParticipantsForm = get_choose_participants_form_factory(group_id)
    if request.method == "POST":
        form = ChooseParticipantsForm(request.POST)
        if form.is_valid():
            bill_participants_account_ids = form.cleaned_data["participants"]
            #bill_participants_account_ids = form.cleaned_data["part"]
            bill_type = form.cleaned_data["bill_type"]
            request.session["bill_participants_account_ids"] = bill_participants_account_ids
            request.session["bill_type"] = bill_type
            request.session["bill_form_part"] = 3
            return HttpResponseRedirect("/bills/bill/create/3/")
    elif request.method == "GET":
        form = ChooseParticipantsForm()
    else:
        return HttpResponse('')
    return render_to_response(
        'bills/bill/create.html', {
            'form': form,
            'derp': "derp",
            'request': request,
            'form_part': 2,
        },
        context_instance=RequestContext(request))


def create_3(request):
    '''
    Now that we have the participants' ids, we
    can construct a form that will allow each persons
    contributions to the bill to be added.

    When the form is posted, we will construct all the proper
    objects to manage the initial accounting for a bill.
    '''
    bill_participants_account_ids = request.session["bill_participants_account_ids"]
    bill_participants = Account.objects.filter(id__in=bill_participants_account_ids)
    if request.method == "POST":
        #Process bill form
        header_form = BillDetailsHeadForm(request.POST)
        participation_formset = ParticipationFormset(request.POST, initial=[{'name': x.user.username, 'account_id': x.id} for x in bill_participants])
        footer_form = BillDetailsFootForm(request.POST)
        #process form
        if header_form.is_valid() and participation_formset.is_valid() and footer_form.is_valid():
            bill_name = header_form.cleaned_data["bill_name"]
            bill_note = footer_form.cleaned_data["bill_note"]
            # schema [account_id, amount_paid]
            line_items = []
            bill_total = Decimal('0.00')
            for f in participation_formset.forms:
                if isinstance(f, ParticipationAmountForm):
                    if f.is_valid():
                        line_items.append([f.cleaned_data["account_id"], f.cleaned_data["amount_paid"]])
                        bill_total += f.cleaned_data["amount_paid"]
            with transaction.commit_on_success():
                new_bill = Bill()
                bill_group = Group.objects.get(pk=request.session["bill_group_id"])
                new_bill.group = bill_group
                new_bill.bill_total = bill_total
                new_bill.name = bill_name
                new_bill.note = bill_note
                new_bill.save()
                participant_count = len(list(line_items))

                obligation_amount = bill_total / participant_count
                debtors_list = []
                creditors_list = []
                overpay_total = Decimal('0.00')
                for item in line_items:
                    bill_participant = BillParticipant()
                    bill_participant.bill = new_bill
                    bill_participant.account_id = item[0]
                    bill_participant.amount_paid = item[1]
                    bill_participant.amount_due = obligation_amount - item[1]
                    bill_participant.save()
                    if item[1] >= obligation_amount:
                        creditors_list.append(item)
                        overpay = item[1] - obligation_amount
                        overpay_total += overpay
                    else:
                        debtors_list.append(item)
                for creditor in creditors_list:
                    creditor_overpay_amount = creditor[1] - obligation_amount
                    if creditor_overpay_amount >= Decimal('0.01'):
                        transaction_list = []
                        for debtor in debtors_list:
                            creditor_weight = creditor_overpay_amount / overpay_total
                            debtor_underpay_amout = obligation_amount - debtor[1]
                            creditor_owed = debtor_underpay_amout * creditor_weight
                            new_transaction = Transaction()
                            new_transaction.bill = new_bill
                            new_transaction.group = bill_group
                            new_transaction.from_account_id = debtor[0]
                            new_transaction.to_account_id = creditor[0]
                            new_transaction.amount = creditor_owed
                            new_transaction.amount_remaining = creditor_owed
                            new_transaction.transfer_type = "D"
                            transaction_list.append(new_transaction)
                        # Check payment
                        paid_total = sum(t.amount for t in transaction_list)
                        debt_owed_diff = creditor_overpay_amount - paid_total
                        if debt_owed_diff != Decimal('0.00'):
                            subtract = False
                            if debt_owed_diff < Decimal('0.00'):
                                debt_owed_diff *= Decimal('-1.00')
                                subtract = True
                            t_count = 0
                            t_len = len(transaction_list)
                            for i in range(0, int(100 * debt_owed_diff)):
                                if subtract:
                                    transaction_list[t_count].amount -= Decimal('0.01')
                                else:
                                    transaction_list[t_count].amount += Decimal('0.01')
                                t_count += 1
                                if t_count >= t_len:
                                    t_count = 0
                        for t in transaction_list:
                            t.save()

            # Successful bill creation means clear the session out
            clear_bill_session(request)
            return HttpResponseRedirect("/bills/dashboard/")
    elif request.method == "GET":
        header_form = BillDetailsHeadForm()
        participation_formset = ParticipationFormset(initial=[{'name': x.user.username, 'account_id': x.id} for x in bill_participants])
        footer_form = BillDetailsFootForm()
    else:
        return HttpResponse("")
    return render_to_response("bills/bill/create_multiform.html",
        {
            "formset" : [header_form, participation_formset, footer_form],
            "form_part": 3,
        },
        context_instance=RequestContext(request))


def handle_create_3_post(header_form, participation_formset, footer_form):
    pass


@login_required
def create(request, form_part="0"):
    '''
    Gateway view, designed to filter the form_part argument
    and then pull the right form portion out of the back end
    Mainly used to clean up the appearance of urls and not directly
    map to a view method, but it also allows add some additional
    validation logic of checking for an existing bill that might
    be incomplete if somebody just goes to the /create/ endpoint.
    Forms under this need to update the session variable "form_part"
    when the form is posted to create_{0} to {0} + 1. This will
    allow the user to resume bill creation from where they might have
    left off at a convenient endpoint
    '''
    try:
        #Make sure this is a valid int
        form_part = int(form_part)
        """
        if form_part is 0, that is the default kwarg (i.e. no arg passed to )
        If they have a bill in progress then send them to a page
        which will allow them to choose whether or not to resume the
        creation
        """
        if form_part == 0:
            if "bill_in_progress" in request.session:
                if request.session["bill_in_progress"]:
                    return HttpResponseRedirect("/bills/bill/start_new_bill/")
            else:
                return HttpResponseRedirect("/bills/bill/create/1/")
        elif form_part > 3:
            form_part = 1
        return (create_1, create_2, create_3)[form_part - 1](request)
    except (ValueError, IndexError) as e:
        print e
        return HttpResponseRedirect("/bills/dashboard/")


# @login_required
# def create(request, form_part=0):
#     if request.method == "POST":
#         # Grab the user account
#         account_id = get_account_id(request)
#         if "form_part" in request.POST.keys():
#             form_part = int(request.POST["form_part"])
#         else:
#             form_part = 0
#         # Depending on the posted formpart, construct the form
#         if form_part == 0:
#             #form = ChoseGroupForm(request.POST, account_id=account_id)
#             pass
#         elif form_part == 1:
#             group_id = request.session.get("group_id", None)
#             if group_id:
#                 #form = ChoseParticipantsForm(request.POST, group_id=group_id, account_id=account_id)
#                 pass
#             else:
#                 # Start them off at the begining
#                 pass
#         elif form_part == 2:
#             write_to_log("request:", request)
#             form = MyFormSet(request.POST)
#             write_to_log("form:", form)
#             for f in form:
#                 write_to_log("form validation_errors:", f.non_field_errors())
#         if form.is_valid():
#             if form_part == 0:
#                 # group selected, now select participants
#                 group_id = form.cleaned_data["groups"]
#                 # set the group id in session
#                 request.session["group_id"] = group_id
#                 # new_form = ChoseParticipantsForm(group_id=group_id, account_id=account_id)
#                 # return render_to_response('bills/bill/create.html',
#                 #     {
#                 #         'form': new_form,
#                 #         'request': request,
#                 #     },
#                 #     context_instance=RequestContext(request))
#             elif form_part == 1:
#                 participant_ids = form.cleaned_data["participants"]
#                 bill_type = form.cleaned_data["bill_type"]
#                 request.session["participants"] = participant_ids
#                 request.session["bill_type"] = bill_type
#                 participants = Account.objects.filter(id__in=participant_ids)
#                 form_set = ParticipationWithDetailsFormset(initial=[{'name': x.user.username, 'account_id': x.id} for x in participants])
#                 return render_to_response('bills/bill/create.html',
#                     {
#                         'form': form_set,
#                         'request': request,
#                     },
#                     context_instance=RequestContext(request))
#             elif form_part == 2:
#                 # Grab the two aggregated forms data
#                 bill_name = request.POST["bill_name"]
#                 print "The bill is: %s" % bill_name
#                 bill_note = request.POST["bill_note"]
#                 group = Group.objects.get(id=request.session["group_id"])
#                 # schema [account_id, amount_paid]
#                 line_items = []
#                 bill_total = Decimal('0.00')
#                 for f in form.forms:
#                     if isinstance(f, ParticipationAmountForm):
#                         if f.is_valid():
#                             line_items.append([f.cleaned_data["account_id"], f.cleaned_data["amount_paid"]])
#                             bill_total += f.cleaned_data["amount_paid"]
#                 with transaction.commit_on_success():
#                     new_bill = Bill()
#                     new_bill.group = group
#                     new_bill.bill_total = bill_total
#                     new_bill.name = bill_name
#                     new_bill.note = bill_note
#                     new_bill.save()
#                     participant_count = len(list(line_items))
#
#                     obligation_amount = bill_total / participant_count
#                     debtors_list = []
#                     creditors_list = []
#                     overpay_total = Decimal('0.00')
#                     for item in line_items:
#                         bill_participant = BillParticipant()
#                         bill_participant.bill = new_bill
#                         bill_participant.account_id = item[0]
#                         bill_participant.amount_paid = item[1]
#                         bill_participant.amount_due = obligation_amount - item[1]
#                         bill_participant.save()
#                         if item[1] >= obligation_amount:
#                             creditors_list.append(item)
#                             overpay = item[1] - obligation_amount
#                             overpay_total += overpay
#                         else:
#                             debtors_list.append(item)
#                     for creditor in creditors_list:
#                         creditor_overpay_amount = creditor[1] - obligation_amount
#                         if creditor_overpay_amount >= Decimal('0.01'):
#                             transaction_list = []
#                             write_to_log("Creditor:",creditor)
#                             write_to_log("overpay:", creditor_overpay_amount)
#                             for debtor in debtors_list:
#                                 creditor_weight = creditor_overpay_amount / overpay_total
#                                 debtor_underpay_amout = obligation_amount - debtor[1]
#                                 creditor_owed = debtor_underpay_amout * creditor_weight
#                                 write_to_log("Debtor:", creditor)
#                                 write_to_log("debtor_underpay_amout:", debtor_underpay_amout)
#                                 write_to_log("Debtor:", creditor)
#                                 write_to_log("creditor_owed:", creditor_owed)
#                                 new_transaction = Transaction()
#                                 new_transaction.bill = new_bill
#                                 new_transaction.group = group
#                                 new_transaction.from_account_id = debtor[0]
#                                 new_transaction.to_account_id = creditor[0]
#                                 new_transaction.amount = creditor_owed
#                                 new_transaction.amount_remaining = creditor_owed
#                                 new_transaction.transfer_type = "D"
#                                 transaction_list.append(new_transaction)
#                             # Check payment
#                             paid_total = sum(t.amount for t in transaction_list)
#                             debt_owed_diff = creditor_overpay_amount - paid_total
#                             write_to_log("paid_total, debt_owed_diff:", (paid_total, debt_owed_diff))
#                             if debt_owed_diff != Decimal('0.00'):
#                                 subtract = False
#                                 if debt_owed_diff < Decimal('0.00'):
#                                     debt_owed_diff *= -1
#                                     subtract = True
#                                 t_count = 0
#                                 t_len = len(transaction_list)
#                                 for i in range(int(100 * debt_owed_diff)):
#                                     if subtract:
#                                         transaction_list[t_count].amount -= Decimal('0.01')
#                                     else:
#                                         transaction_list[t_count].amount += Decimal('0.01')
#                                     t_count += 1
#                                     if t_count >= t_len:
#                                         t_count = 0
#                             for t in transaction_list:
#                                 t.save()
#
#                 return HttpResponseRedirect(reverse("bills.views.dashboard"))
#         else:
#             return render_to_response('bills/bill/create.html',
#                 {
#                     'form': form,
#                     'request': request,
#                 },
#                 context_instance=RequestContext(request))
#     elif request.method == "GET":
#         # build start of form
#         pass
#     form = ChoseGroupForm(account_id=get_account_id(request))
#     return render_to_response('bills/bill/create.html', {
#             'form': form,
#             'request': request,
#         },
#         context_instance=RequestContext(request))

# from pprint import pprint
#
#
# def write_to_log(message, obj):
#     with open("log.txt", "a") as f:
#         f.write(message + " :\n")
#         f.write(str(obj) + "\n")
