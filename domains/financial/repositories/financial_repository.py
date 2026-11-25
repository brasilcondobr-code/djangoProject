from django.db.models import Sum

from domains.financial.models import (
    Agreement, PaymentSlip, Cash, Collection, Shopping, Loan,
    NewRelease, Payment, CollectionCredit, Apportionment, Receipt,
    BankTransfer
)


class FinancialRepository:
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
    def get_collection_by_id(collection_id):
        try:
            return Collection.objects.select_related(
                "condominium",
                "condominium__condominium",
                "created_by",
                "updated_by",
            ).get(pk=collection_id)
        except Collection.DoesNotExist:
            return None

    @staticmethod
    def get_collection_for_update(collection_id):
        """Obtém a cobrança com bloqueio de linha (exige transação ativa)."""
        return Collection.objects.select_for_update().get(pk=collection_id)

    @staticmethod
    def get_collection_new_releases(collection_id):
        return NewRelease.objects.filter(
            collection_id=collection_id
        ).select_related(
            "condominium",
            "condominium__condominium",
            "chartOfAccounts",
            "fund",
        ).order_by("launchDate", "id")

    @staticmethod
    def get_collection_credits(collection_id):
        return CollectionCredit.objects.filter(
            collection_id=collection_id
        ).select_related(
            "financialTransaction",
            "created_by",
            "updated_by",
        ).order_by("creditDate", "id")

    @staticmethod
    def get_collection_payments(collection_id):
        return Payment.objects.filter(
            collection_id=collection_id
        ).select_related(
            "financialTransaction",
            "created_by",
            "updated_by",
        ).order_by("dateReceived", "id")

    @staticmethod
    def get_collection_payments_total(collection_id):
        total = Payment.objects.filter(
            collection_id=collection_id
        ).aggregate(total=Sum("amountReceived"))["total"]
        return total or 0

    @staticmethod
    def get_collection_credits_total(collection_id):
        total = CollectionCredit.objects.filter(
            collection_id=collection_id
        ).aggregate(total=Sum("amountCredit"))["total"]
        return total or 0

    @staticmethod
    def set_collection_error_status(collection_id, message):
        """Grava o erro fora do savepoint que falhou."""
        return Collection.objects.filter(pk=collection_id).update(
            errorStatus=message
        )

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
    def get_new_release_by_id(new_release_id):
        try:
            return NewRelease.objects.select_related(
                "condominium",
                "condominium__condominium",
                "paymaster",
                "chartOfAccounts",
                "fund",
                "created_by",
                "updated_by",
            ).get(pk=new_release_id)
        except NewRelease.DoesNotExist:
            return None

    @staticmethod
    def get_new_release_for_update(new_release_id):
        """Obtém o lançamento com bloqueio de linha (exige transação ativa)."""
        return NewRelease.objects.select_for_update().get(pk=new_release_id)

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
