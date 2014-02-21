from django.contrib import admin
from .models import Account, Transaction, Bill, BillParticipant, Group


class AccountAdmin(admin.ModelAdmin):
    pass


class BillParticipantInline(admin.TabularInline):
    model = BillParticipant
    extra = 0
    exclude = ("amount_due", )


class BillAdmin(admin.ModelAdmin):
    inlines = [
        BillParticipantInline,
    ]


admin.site.register(Account, AccountAdmin)
admin.site.register(Group)
admin.site.register(Transaction)
admin.site.register(Bill, BillAdmin)
admin.site.register(BillParticipant)
