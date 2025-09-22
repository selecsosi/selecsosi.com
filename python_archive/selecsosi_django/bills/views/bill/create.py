from decimal import Decimal, ROUND_HALF_DOWN, localcontext

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext

from ...forms import ParticipationAmountForm, BillDetailsFootForm, ParticipationFormset, BillDetailsHeadForm, get_choose_participants_form_factory, get_choose_group_form_factory
from ...forms import StartNewBillForm
from ...models import Transaction, BillParticipant, Bill, Account, Group

@login_required
def index(request, form_part="0"):
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


def create_1(request):
    """
    First step in the create bill process, user
    must choose a group that they are a member of
    that the bill took place between. Groups are a method
    or corralling the users bill space and only billing
    specific users that have consented
    """
    account_id = _get_account_id(request)
    ChooseGroupForm = get_choose_group_form_factory(account_id)
    if request.method == "POST":
        form = ChooseGroupForm(request.POST)
        if form.is_valid():
            group_id = form.cleaned_data["group"]
            # set the group id in session to be used in the next part
            request.session["bill_group_id"] = group_id
            #update the completed form_part
            request.session["bill_form_part"] = 2
            request.session["bill_in_progress"] = True
            return HttpResponseRedirect("/bills/bill/create/2/")
    else:
        form = ChooseGroupForm()

    return render_to_response(
        'bill/create.html', {
            "title" : "Pick The Group",
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
    if "bill_group_id" in request.session:
        group_id = request.session["bill_group_id"]
    else:
        return HttpResponseRedirect("/bills/dashboard/")

    ChooseParticipantsForm = get_choose_participants_form_factory(group_id)
    if request.method == "POST":
        form = ChooseParticipantsForm(request.POST)
        if form.is_valid():
            bill_participants_account_ids = form.cleaned_data["participants"]
            bill_type = form.cleaned_data["bill_type"]
            request.session["bill_participants_account_ids"] = bill_participants_account_ids
            request.session["bill_type"] = bill_type
            request.session["bill_form_part"] = 3
            return HttpResponseRedirect("/bills/bill/create/3/")

    else:
        form = ChooseParticipantsForm()

    return render_to_response(
        'bill/create.html', {
            "title" : "Choose Participants",
            'form': form,
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
    if "bill_participants_account_ids" in request.session:
        bill_participants_account_ids = request.session["bill_participants_account_ids"]
    else:
        return HttpResponseRedirect("/bills/dashboard/")
    bill_participants = Account.objects.filter(id__in=bill_participants_account_ids)
    if request.method == "POST":
        #Process bill form
        header_form = BillDetailsHeadForm(request.POST)
        participation_formset = ParticipationFormset(request.POST,
            initial=[{'name': x.user.username, 'account_id': x.id} for x in bill_participants])
        footer_form = BillDetailsFootForm(request.POST)
        # Process the form
        if header_form.is_valid() and participation_formset.is_valid() and footer_form.is_valid():
            bill_group = Group.objects.get(pk=request.session["bill_group_id"])
            bill_name = header_form.cleaned_data["bill_name"]
            bill_note = footer_form.cleaned_data["bill_note"]
            if request.session["bill_type"] == "E":
                _process_even_split_bill_form(bill_name, bill_group, bill_note, participation_formset)

            # Successful bill creation means clear the session out
            _clear_bill_session(request)
            return HttpResponseRedirect("/bills/dashboard/")
    else:
        header_form = BillDetailsHeadForm()
        participation_formset = ParticipationFormset(
            initial=[{'name': x.user.username, 'account_id': x.id} for x in bill_participants])
        footer_form = BillDetailsFootForm()

    return render_to_response("bill/create_multiform.html",
        {
            "title" : "Bill Details",
            "formset" : [header_form, participation_formset, footer_form],
            "form_part": 3,
        },
        context_instance=RequestContext(request))


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
                _clear_bill_session(request)
                return HttpResponseRedirect("/bills/bill/create/1/")
            else:
                return HttpResponseRedirect("/bills/bill/create/%s/" % request.session["bill_form_part"])

    elif request.method == "GET":
        form = StartNewBillForm()
        return render_to_response(
            "bill/start_new_bill.html", {
            "form": form,
            },
            context_instance=RequestContext(request))


def _get_account_id(request):
    account_id = request.session.get("account_id", None)
    if not account_id:
        user = request.user
        user_account = Account.objects.get(user__id=user.id)
        account_id = user_account.id
        request.session["account_id"] = account_id
    return account_id


def _clear_bill_session(request):
    # Clear out any other bill
    for k in request.session.keys():
        if k.startswith("bill"):
            del request.session[k]


def _create_new_bill(name, group, total, note):
    with transaction.atomic():
        new_bill = Bill()
        new_bill.group = group
        new_bill.bill_total = total
        new_bill.name = name
        new_bill.note = note
        new_bill.save()
        return new_bill

def _process_even_split_bill_form(bill_name, bill_group, bill_note, participation_formset):
    with localcontext() as ctx:
        ctx.rounding = ROUND_HALF_DOWN
        # Reference the group
        participation_list = _parse_even_split_participation(participation_formset)
        bill_total = sum(x[1] for x in participation_list)
        new_bill = _create_new_bill(bill_name, bill_group, bill_total, bill_note)
        participant_count = len(participation_list)
        # Get the amount each party should pay by evenly dividing the total
        participant_due_amount = Decimal(bill_total / participant_count).quantize(Decimal("0.01"))
        # Assemble two lists, one of creditors, one of debtors
        overpay_total, creditors_list, debtors_list = _construct_participation(participation_list,
                                                                               new_bill,
                                                                               participant_due_amount)
        _create_bill_transactions(creditors_list, debtors_list, participant_due_amount, overpay_total, new_bill, bill_group)


def _construct_participation(participation_list, new_bill, participant_due_amount):
    overpay_total = Decimal('0.00')
    creditors_list = []
    debtors_list = []
    for account_id, amount_paid in participation_list:
        bill_participant = BillParticipant()
        bill_participant.bill = new_bill
        bill_participant.account_id = account_id
        bill_participant.amount_paid = amount_paid
        bill_participant.amount_due = participant_due_amount - amount_paid
        if amount_paid >= participant_due_amount:
            creditors_list.append(bill_participant)
            overpay = amount_paid - participant_due_amount
            overpay_total += overpay
        else:
            debtors_list.append(bill_participant)

    return overpay_total, creditors_list, debtors_list

def _create_bill_transactions(creditors_list, debtors_list, participant_due_amount, overpay_total, new_bill, bill_group):
    with transaction.atomic():
        # Do a round robbin assigning debts out to people for each creditor
        for creditor in creditors_list:
            creditor_overpay_amount = creditor.amount_paid - participant_due_amount
            if creditor_overpay_amount >= Decimal('0.01'):
                transaction_list = []
                for debtor in debtors_list:
                    creditor_weight = creditor_overpay_amount / overpay_total
                    debtor_underpay_amount = participant_due_amount - debtor.amount_paid
                    creditor_owed = Decimal(debtor_underpay_amount * creditor_weight).quantize(Decimal("0.01"))
                    new_transaction = Transaction()
                    new_transaction.bill = new_bill
                    new_transaction.note = new_bill.note
                    new_transaction.group = bill_group
                    new_transaction.from_account_id = debtor.account_id
                    new_transaction.to_account_id = creditor.account_id
                    new_transaction.amount = creditor_owed
                    new_transaction.amount_remaining = creditor_owed
                    new_transaction.transfer_type = "D"
                    transaction_list.append([new_transaction, debtor])
                # Check payment
                paid_total = sum(t[0].amount for t in transaction_list)
                # Check for debt over/under pay
                debt_owed_diff = creditor_overpay_amount - paid_total
                if debt_owed_diff != Decimal('0.00'):
                    subtract = False
                    if debt_owed_diff < Decimal('0.00'):
                        debt_owed_diff *= Decimal('-1.00')
                        subtract = True
                    t_count = 0
                    t_len = len(transaction_list)
                    for i in xrange(0, int(100 * debt_owed_diff)):
                        if subtract:
                            transaction_list[t_count][0].amount -= Decimal('0.01')
                            transaction_list[t_count][0].amount_remaining -= Decimal('0.01')
                            #Update the bill participant
                            transaction_list[t_count][1].amount_due -= Decimal('0.01')
                        else:
                            transaction_list[t_count][0].amount += Decimal('0.01')
                            transaction_list[t_count][0].amount_remaining += Decimal('0.01')
                            #Update the bill participant
                            transaction_list[t_count][1].amount_due += Decimal('0.01')
                        t_count += 1
                        if t_count >= t_len:
                            t_count = 0
                for t in transaction_list:
                    t[0].save()
                    t[1].save()
                for creditor in creditors_list:
                    creditor.save()

def _parse_even_split_participation(formset):
    """
    :param formset: the ParticipationFormset that is posted to the endpoint
    :rtype : bill_total, participation_list
    participation_list schema: [ account_id, amount_paid ]
    """
    participation_list = []
    for f in formset.forms:
        if isinstance(f, ParticipationAmountForm):
            if f.is_valid():
                participation_list.append([f.cleaned_data["account_id"], f.cleaned_data["amount_paid"]])
    return participation_list

def _parse_itemized_participation(formset):
    pass