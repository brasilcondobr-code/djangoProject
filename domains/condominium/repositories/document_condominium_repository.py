from domains.condominium.models import DocumentCondominium

class DocumentCondominiumRepository:
    @staticmethod
    def get_by_id(id):
        try:
            return DocumentCondominium.objects.get(pk=id)
        except DocumentCondominium.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return DocumentCondominium.objects.all()

    @staticmethod
    def get_by_condominium(condominium):
        return DocumentCondominium.objects.filter(condominium=condominium)

    @staticmethod
    def create(data):
        document = DocumentCondominium(**data)
        document.save()
        return document

    @staticmethod
    def update(document, data):
        for key, value in data.items():
            setattr(document, key, value)
        document.save()
        return document

    @staticmethod
    def delete(document):
        document.delete()
