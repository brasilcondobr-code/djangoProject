from domains.administrative.repositories import BankRepository
from domains.administrative.selectors import BankSelector

class BankService:
    @staticmethod
    def create_bank(data):
        return BankRepository.create(data)

    @staticmethod
    def update_bank(bank_id, data):
        bank = BankRepository.get_by_id(bank_id)
        if bank:
            return BankRepository.update(bank, data)
        return None

    @staticmethod
    def delete_bank(bank_id):
        bank = BankRepository.get_by_id(bank_id)
        if bank:
            BankRepository.delete(bank)
            return True
        return False

    @staticmethod
    def get_all_banks():
        return BankSelector.get_all()

    @staticmethod
    def get_bank_by_id(id):
        return BankSelector.get_by_id(id)
