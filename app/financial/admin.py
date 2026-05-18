from django.contrib import admin
from .models import (
    Agreement, PaymentSlip, Cash, Collection, Shopping, 
    Loan, NewRelease, Payment, Apportionment, Receipt, BankTransfer
)

@admin.register(Agreement)
class AgreementAdmin(admin.ModelAdmin):
    pass

@admin.register(PaymentSlip)
class PaymentSlipAdmin(admin.ModelAdmin):
    pass

@admin.register(Cash)
class CashAdmin(admin.ModelAdmin):
    pass

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    pass

@admin.register(Shopping)
class ShoppingAdmin(admin.ModelAdmin):
    pass

@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    pass

@admin.register(NewRelease)
class NewReleaseAdmin(admin.ModelAdmin):
    pass

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass

@admin.register(Apportionment)
class ApportionmentAdmin(admin.ModelAdmin):
    pass

@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):
    pass

@admin.register(BankTransfer)
class BankTransferAdmin(admin.ModelAdmin):
    pass
