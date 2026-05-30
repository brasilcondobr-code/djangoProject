from domains.administrative.models.bank import Bank

class BankSelector:
    @staticmethod
    def get_all():
        return Bank.objects.all()

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
