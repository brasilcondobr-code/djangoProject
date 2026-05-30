from domains.financial.repositories import FinancialRepository
from domains.financial.selectors import FinancialSelector

class FinancialService:
    @staticmethod
    def get_all_agreements():
        return FinancialSelector.get_all_agreements()

    @staticmethod
    def get_all_payment_slips():
        return FinancialSelector.get_all_payment_slips()

    @staticmethod
    def get_all_cash():
        return FinancialSelector.get_all_cash()

    @staticmethod
    def get_all_collections():
        return FinancialSelector.get_all_collections()

    @staticmethod
    def get_all_shoppings():
        return FinancialSelector.get_all_shoppings()

    @staticmethod
    def get_all_loans():
        return FinancialSelector.get_all_loans()

    @staticmethod
    def get_all_new_releases():
        return FinancialSelector.get_all_new_releases()

    @staticmethod
    def get_all_payments():
        return FinancialSelector.get_all_payments()

    @staticmethod
    def get_all_apportionments():
        return FinancialSelector.get_all_apportionments()

    @staticmethod
    def get_all_receipts():
        return FinancialSelector.get_all_receipts()

    @staticmethod
    def get_all_bank_transfers():
        return FinancialSelector.get_all_bank_transfers()
