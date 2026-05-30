from domains.parameters.repositories.types_condominium_repository import TypesCondominiumRepository
from domains.parameters.repositories.struction_condominium_repository import StructionCondominiumRepository
from domains.parameters.repositories.states_repository import StatesRepository
from domains.parameters.repositories.addresses_repository import AddressesRepository
from domains.parameters.repositories.types_visitor_restrictions_repository import TypesVisitorRestrictionsRepository
from domains.parameters.repositories.resident_type_repository import ResidentTypeRepository

class ParametersService:
    @staticmethod
    def create_type_condominium(data):
        return TypesCondominiumRepository.create(data)

    @staticmethod
    def update_type_condominium(type_condominium, data):
        return TypesCondominiumRepository.update(type_condominium, data)

    @staticmethod
    def delete_type_condominium(type_condominium):
        return TypesCondominiumRepository.delete(type_condominium)

    @staticmethod
    def create_struction_condominium(data):
        return StructionCondominiumRepository.create(data)

    @staticmethod
    def update_struction_condominium(struction_condominium, data):
        return StructionCondominiumRepository.update(struction_condominium, data)

    @staticmethod
    def delete_struction_condominium(struction_condominium):
        return StructionCondominiumRepository.delete(struction_condominium)

    @staticmethod
    def create_state(data):
        return StatesRepository.create(data)

    @staticmethod
    def update_state(state, data):
        return StatesRepository.update(state, data)

    @staticmethod
    def delete_state(state):
        return StatesRepository.delete(state)

    @staticmethod
    def create_address(data):
        return AddressesRepository.create(data)

    @staticmethod
    def update_address(address, data):
        return AddressesRepository.update(address, data)

    @staticmethod
    def delete_address(address):
        return AddressesRepository.delete(address)

    @staticmethod
    def create_type_visitor_restriction(data):
        return TypesVisitorRestrictionsRepository.create(data)

    @staticmethod
    def update_type_visitor_restriction(type_visitor_restriction, data):
        return TypesVisitorRestrictionsRepository.update(type_visitor_restriction, data)

    @staticmethod
    def delete_type_visitor_restriction(type_visitor_restriction):
        return TypesVisitorRestrictionsRepository.delete(type_visitor_restriction)

    @staticmethod
    def create_resident_type(data):
        return ResidentTypeRepository.create(data)

    @staticmethod
    def update_resident_type(resident_type, data):
        return ResidentTypeRepository.update(resident_type, data)

    @staticmethod
    def delete_resident_type(resident_type):
        return ResidentTypeRepository.delete(resident_type)
