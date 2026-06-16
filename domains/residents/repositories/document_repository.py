from domains.residents.models import Documents

class DocumentsRepository:
    @staticmethod
    def get_by_id(id):
        try:
            return Documents.objects.get(pk=id)
        except Documents.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return Documents.objects.all()

    @staticmethod
    def get_by_unit(unit):
        return Documents.objects.filter(condo_unit=unit)

    @staticmethod
    def create(data):
        document = Documents(**data)
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
