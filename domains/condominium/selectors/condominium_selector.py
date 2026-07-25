from shared.selectors import BaseSelector
from domains.condominium.models import Condominium


class CondominiumSelector(BaseSelector):
    model = Condominium

    @classmethod
    def get_by_code(cls, code):
        return cls.model.objects.filter(code=code).first()

    @classmethod
    def get_by_cnpj(cls, cnpj):
        return cls.model.objects.filter(cnpj=cnpj).first()
