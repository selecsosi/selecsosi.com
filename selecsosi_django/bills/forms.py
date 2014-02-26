from decimal import *

from django import forms
from django.forms.widgets import HiddenInput
from django.forms.formsets import BaseFormSet, formset_factory
from .models import Account, Group

from django.core.exceptions import ValidationError


def validate_group_choice(value):
    if value is not '':
        try:
            val = int(value)
        except ValueError:
            raise ValidationError('Please select a group')
    else:
        raise ValidationError('Please select a group')


def get_choose_group_form_factory(account_id):
    user_account = Account.objects.get(id=account_id)
    groups = Group.objects.filter(accounts=user_account)
    choices = [("", "Plese Select")]
    for group in groups:
        choices.append((group.id, group.name))

    if len(groups) > 0:
        class ChooseGroupForm(forms.Form):
            group = forms.ChoiceField(choices=choices, validators=[validate_group_choice,], initial=groups[0].id)

        return ChooseGroupForm


def get_choose_participants_form_factory(group_id):
    group_participants = Group.objects.get(pk=group_id).accounts.all()
    choices = [(p.id, p.user.username) for p in group_participants]
    TYPE_CHOICES = (
        ('E', 'Even Split'),
        ('L', 'Line Item')
    )

    class ChooseParticipantsForm(forms.Form):
        participants = forms.MultipleChoiceField(choices=choices)
        #part = forms.MultipleChoiceField(label="participants", choices=choices)
        bill_type = forms.ChoiceField(choices=TYPE_CHOICES)
    return ChooseParticipantsForm


class StartNewBillForm(forms.Form):
    start_over = forms.BooleanField("Start Over")


class ParticipationAmountForm(forms.Form):
    # name = forms.CharField(widget=HiddenInput)
    account_id = forms.IntegerField(widget=HiddenInput)
    amount_paid = forms.DecimalField(decimal_places=2, required=True, min_value=Decimal("0.00"))

    def __init__(self, *args, **kwargs):
        super(ParticipationAmountForm, self).__init__(*args, **kwargs)
        if "initial" in kwargs.keys():
            self.fields["amount_paid"].label = kwargs["initial"]["name"] + " paid"


class BillDetailsHeadForm(forms.Form):
    bill_name = forms.CharField(required=False)


class BillDetailsFootForm(forms.Form):
    bill_note = forms.CharField(widget=forms.Textarea, required=False)


class ParticipationAmountFormSet(BaseFormSet):
    """
    Formset that passes the HttpRequest on to every Form's __init__
    Suitable to populate Fields dynamically depending on request
    """
    def __init__(self, *args, **kwargs):
        super(ParticipationAmountFormSet, self).__init__(*args, **kwargs)  # this calls _construct_forms()

    def _construct_forms(self):  # this one is merely taken from django's BaseFormSet
        # except the additional request parameter for the Form-constructor
        self.forms = []
        self.forms.append(BillDetailsHeadForm())
        for i in xrange(self.total_form_count()):
            self.forms.append(self._construct_form(i))
        self.forms.append(BillDetailsFootForm())


ParticipationFormset = formset_factory(ParticipationAmountForm, extra=0)


# class ChoseToAccountForm(forms.Form):
#     to_account = forms.ChoiceField()
#     form_part = forms.IntegerField(widget=HiddenInput, initial=0)
#
#     def __init__(self, *args, **kwargs):
#         super(ChoseToAccountForm, self).__init__(*args, **kwargs)
#         choices = kwargs["initial"]["to_account"]["choices"]
#         self.fields["to_account"].choices = choices
#         self.fields["to_account"].initial = choices[0][0]

# class PaymentForm(forms.Form):
    
#     bill = forms.ChoiceField(required=False)
#     current_amount_due = forms.DecimalField(decimal_places=2)
#     payment_amount = forms.DecimalField(decimal_places=2)

#     def __init__(self, *args, **kwargs):
#         account_id = kwargs.pop("account_id", None)
#         super(ChoseGroupForm, self).__init__(*args, **kwargs)
#         if account_id:
#             user_account = Account.objects.get(id=account_id)
#             groups = Group.objects.filter(accounts=user_account)
#             choices = [("", "Plese Select")] + [(group.id, group.name) for group in groups]
#             self.fields["groups"].choices = choices
#             self.fields["groups"].initial = choices[0][0]
