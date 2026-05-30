from django.core.exceptions import ObjectDoesNotExist
from domains.condominium.models import Condominium

class CondominiumRepository:
    @staticmethod
    def get_by_id(id):
        try:
            return Condominium.objects.get(pk=id)
        except Condominium.DoesNotExist:
            return None

    @staticmethod
    def get_by_code(code):
        try:
            return Condominium.objects.get(code=code)
        except Condominium.DoesNotExist:
            return None

    @staticmethod
    def get_by_cnpj(cnpj):
        try:
            return Condominium.objects.get(cnpj=cnpj)
        except Condominium.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return Condominium.objects.all()

    @staticmethod
    def get_active():
        return Condominium.objects.filter(is_active=True)

    @staticmethod
    def create(data):
        condominium = Condominium(**data)
        condominium.save()
        return condominium

    @staticmethod
    def update(condominium, data):
        for key, value in data.items():
            setattr(condominium, key, value)
        condominium.save()
        return condominium

    @staticmethod
    def delete(condominium):
        condominium.delete()
