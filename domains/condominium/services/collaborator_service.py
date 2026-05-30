from domains.condominium.repositories import CollaboratorRepository
from domains.condominium.selectors import CollaboratorSelector

class CollaboratorService:
    @staticmethod
    def create_collaborator(data):
        return CollaboratorRepository.create(data)

    @staticmethod
    def update_collaborator(collaborator_id, data):
        collaborator = CollaboratorRepository.get_by_id(collaborator_id)
        if collaborator:
            return CollaboratorRepository.update(collaborator, data)
        return None

    @staticmethod
    def activate_collaborator(collaborator_id):
        collaborator = CollaboratorRepository.get_by_id(collaborator_id)
        if collaborator:
            CollaboratorRepository.update(collaborator, {'is_active': True})
            return True
        return False

    @staticmethod
    def deactivate_collaborator(collaborator_id):
        collaborator = CollaboratorRepository.get_by_id(collaborator_id)
        if collaborator:
            CollaboratorRepository.update(collaborator, {'is_active': False})
            return True
        return False

    @staticmethod
    def delete_collaborator(collaborator_id):
        collaborator = CollaboratorRepository.get_by_id(collaborator_id)
        if collaborator:
            CollaboratorRepository.delete(collaborator)
            return True
        return False

    @staticmethod
    def get_collaborator_details(collaborator_id):
        return CollaboratorSelector.get_by_id(collaborator_id)
