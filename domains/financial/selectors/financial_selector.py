from domains.financial.models import (
    Agreement, PaymentSlip, Cash, Collection, Shopping, Loan, 
    NewRelease, Payment, Apportionment, Receipt, BankTransfer
)

class FinancialSelector:
    @staticmethod
    def get_all_agreements():
        return Agreement.objects.all()

    @staticmethod
    def get_all_payment_slips():
        return PaymentSlip.objects.all()

    @staticmethod
    def get_all_cash():
        return Cash.objects.all()

    @staticmethod
    def get_all_collections():
        return Collection.objects.all()

    @staticmethod
    def get_all_shoppings():
        return Shopping.objects.all()

    @staticmethod
    def get_all_loans():
        return Loan.objects.all()

    @staticmethod
    def get_all_new_releases():
        return NewRelease.objects.all()

    @staticmethod
    def get_all_payments():
        return Payment.objects.all()

    @staticmethod
    def get_all_apportionments():
        return Apportionment.objects.all()

    @staticmethod
    def get_all_receipts():
        return Receipt.objects.all()

    @staticmethod
    def get_all_bank_transfers():
        return BankTransfer.objects.all()
