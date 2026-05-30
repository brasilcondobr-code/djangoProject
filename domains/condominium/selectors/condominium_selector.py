from domains.condominium.models import Condominium

class CondominiumSelector:
    @staticmethod
    def get_all_active():
        return Condominium.objects.filter(is_active=True)

    @staticmethod
    def get_by_id(id):
        return Condominium.objects.filter(pk=id).first()

    @staticmethod
    def get_by_code(code):
        return Condominium.objects.filter(code=code).first()

    @staticmethod
    def get_by_cnpj(cnpj):
        return Condominium.objects.filter(cnpj=cnpj).first()
