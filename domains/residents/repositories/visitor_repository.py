from domains.residents.models import Visitor

class VisitorRepository:
    @staticmethod
    def get_by_id(id):
        try:
            return Visitor.objects.get(pk=id)
        except Visitor.DoesNotExist:
            return None

    @staticmethod
    def list_all():
        return Visitor.objects.all()

    @staticmethod
    def create(data):
        visitor = Visitor(**data)
        visitor.save()
        return visitor

    @staticmethod
    def update(visitor, data):
        for key, value in data.items():
            setattr(visitor, key, value)
        visitor.save()
        return visitor

    @staticmethod
    def delete(visitor):
        visitor.delete()
