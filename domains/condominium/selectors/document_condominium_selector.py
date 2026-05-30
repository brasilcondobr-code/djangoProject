from domains.condominium.models import DocumentCondominium

class DocumentCondominiumSelector:
    @staticmethod
    def get_all():
        return DocumentCondominium.objects.all()

    @staticmethod
    def get_by_id(id):
        return DocumentCondominium.objects.filter(pk=id).first()

    @staticmethod
    def get_by_condominium(condominium):
        return DocumentCondominium.objects.filter(condominium=condominium)
