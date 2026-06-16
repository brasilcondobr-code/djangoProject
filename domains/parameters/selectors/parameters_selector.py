from domains.parameters.models import TypesCondominium, StructionCondominium, States, Addresses, TypesVisitorRestrictions, ResidentType

class ParametersSelector:
    @staticmethod
    def get_all_types_condominium():
        return TypesCondominium.objects.all()

    @staticmethod
    def get_type_condominium_by_id(id):
        try:
            return TypesCondominium.objects.get(pk=id)
        except TypesCondominium.DoesNotExist:
            return None

    @staticmethod
    def get_all_struction_condominium():
        return StructionCondominium.objects.all()

    @staticmethod
    def get_struction_condominium_by_id(id):
        try:
            return StructionCondominium.objects.get(pk=id)
        except StructionCondominium.DoesNotExist:
            return None

    @staticmethod
    def get_all_states():
        return States.objects.all()

    @staticmethod
    def get_state_by_abbreviation(abbreviation):
        try:
            return States.objects.get(abbreviation=abbreviation)
        except States.DoesNotExist:
            return None

    @staticmethod
    def get_all_addresses():
        return Addresses.objects.all()

    @staticmethod
    def get_address_by_zip_code(zip_code):
        try:
            return Addresses.objects.get(zip_code=zip_code)
        except Addresses.DoesNotExist:
            return None

    @staticmethod
    def get_all_types_visitor_restrictions():
        return TypesVisitorRestrictions.objects.all()

    @staticmethod
    def get_type_visitor_restriction_by_id(id):
        try:
            return TypesVisitorRestrictions.objects.get(pk=id)
        except TypesVisitorRestrictions.DoesNotExist:
            return None

    @staticmethod
    def get_all_resident_types():
        return ResidentType.objects.all()

    @staticmethod
    def get_resident_type_by_id(id):
        try:
            return ResidentType.objects.get(pk=id)
        except ResidentType.DoesNotExist:
            return None
