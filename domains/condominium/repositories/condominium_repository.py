from shared.repositories import BaseRepository
from domains.condominium.models import Condominium


class CondominiumRepository(BaseRepository):
    model = Condominium

    @classmethod
    def get_by_code(cls, code):
        try:
            return cls.model.objects.get(code=code)
        except cls.model.DoesNotExist:
            return None

    @classmethod
    def get_by_cnpj(cls, cnpj):
        try:
            return cls.model.objects.get(cnpj=cnpj)
        except cls.model.DoesNotExist:
            return None
