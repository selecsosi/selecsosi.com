from decimal import *

from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    user = models.ForeignKey(User)
    account_balance = models.DecimalField("Account Balance", max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Group(models.Model):
    name = models.CharField("Group Name", max_length=256)
    accounts = models.ManyToManyField(Account)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Bill(models.Model):
    group = models.ForeignKey(Group)
    name = models.CharField(max_length=256)
    bill_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    note = models.TextField("Note")
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Total: $%0.2f" % self.bill_total


class BillParticipant(models.Model):
    bill = models.ForeignKey(Bill)
    account = models.ForeignKey(Account)
    amount_paid = models.DecimalField("Amount Paid", max_digits=10, decimal_places=2)
    amount_due = models.DecimalField("Amount Due", max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        due = Decimal(0.00)
        if self.amount_due > 0:
            due = self.amount_due
        return "%s - %s - due: $%0.2f" % (self.created, self.account.user.username, due)


class Transaction(models.Model):
    '''
    Ledger Entries
    '''
    TRANSACTION_CHOICES = (
        ("D", "Debit"),
        ("C", "Credit"),
    )
    bill = models.ForeignKey(Bill, null=True, blank=True, related_name='bill+')
    group = models.ForeignKey(Group, verbose_name=u'Group')
    from_account = models.ForeignKey(Account, verbose_name="From", related_name='from_account')
    to_account = models.ForeignKey(Account, verbose_name="To", related_name='to_account')
    amount = models.DecimalField("Amount", max_digits=10, decimal_places=2)
    note = models.TextField("Note", blank=True, null=True)
    transfer_type = models.CharField("Type", choices=TRANSACTION_CHOICES, max_length=2)
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now_add=True)
    # Tag for transactions to reference if they are in repayment (optional)
    original_transaction = models.ForeignKey('self', null=True, blank=True)

    def __str__(self):
        return "%s - %s -> %s - amount: $%0.2f" % (self.transfer_type, self.from_account.user.username, self.to_account.user.username, self.amount)
