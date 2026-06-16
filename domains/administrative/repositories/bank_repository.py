from domains.administrative.models.bank import Bank

class BankRepository:
    @staticmethod
    def get_by_id(id):
        try:
            return Bank.objects.get(pk=id)
        except Bank.DoesNotExist:
            return None

    @staticmethod
    def get_by_compe_and_agency(compe, agency):
        try:
            return Bank.objects.get(compe=compe, agency=agency)
        except Bank.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return Bank.objects.all()

    @staticmethod
    def create(data):
        bank = Bank(**data)
        bank.save()
        return bank

    @staticmethod
    def update(bank, data):
        for key, value in data.items():
            setattr(bank, key, value)
        bank.save()
        return bank

    @staticmethod
    def delete(bank):
        bank.delete()
