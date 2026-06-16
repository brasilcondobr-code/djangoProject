from domains.parameters.models import TypesVisitorRestrictions

class TypesVisitorRestrictionsRepository:
    @staticmethod
    def get_all():
        return TypesVisitorRestrictions.objects.all()

    @staticmethod
    def get_by_id(id):
        try:
            return TypesVisitorRestrictions.objects.get(pk=id)
        except TypesVisitorRestrictions.DoesNotExist:
            return None

    @staticmethod
    def create(data):
        types_visitor_restrictions = TypesVisitorRestrictions(**data)
        types_visitor_restrictions.save()
        return types_visitor_restrictions

    @staticmethod
    def update(types_visitor_restrictions, data):
        for key, value in data.items():
            setattr(types_visitor_restrictions, key, value)
        types_visitor_restrictions.save()
        return types_visitor_restrictions

    @staticmethod
    def delete(types_visitor_restrictions):
        types_visitor_restrictions.delete()
