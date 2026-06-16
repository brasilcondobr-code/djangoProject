from domains.condominium.repositories import CondominiumRepository
from domains.condominium.selectors import CondominiumSelector

class CondominiumService:
    @staticmethod
    def create_condominium(data):
        return CondominiumRepository.create(data)

    @staticmethod
    def update_condominium(condominium_id, data):
        condominium = CondominiumRepository.get_by_id(condominium_id)
        if condominium:
            return CondominiumRepository.update(condominium, data)
        return None

    @staticmethod
    def activate_condominium(condominium_id):
        condominium = CondominiumRepository.get_by_id(condominium_id)
        if condominium:
            CondominiumRepository.update(condominium, {'is_active': True})
            return True
        return False

    @staticmethod
    def deactivate_condominium(condominium_id):
        condominium = CondominiumRepository.get_by_id(condominium_id)
        if condominium:
            CondominiumRepository.update(condominium, {'is_active': False})
            return True
        return False

    @staticmethod
    def delete_condominium(condominium_id):
        condominium = CondominiumRepository.get_by_id(condominium_id)
        if condominium:
            CondominiumRepository.delete(condominium)
            return True
        return False

    @staticmethod
    def get_condominium_details(condominium_id):
        return CondominiumSelector.get_by_id(condominium_id)
