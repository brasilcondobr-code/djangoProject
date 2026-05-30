from domains.personalities.repositories import EntityRepository
from domains.personalities.selectors import EntitySelector

class EntityService:
    @staticmethod
    def create_entity(data):
        return EntityRepository.create(data)

    @staticmethod
    def update_entity(entity_id, data):
        entity = EntityRepository.get_by_id(entity_id)
        if entity:
            return EntityRepository.update(entity, data)
        return None

    @staticmethod
    def delete_entity(entity_id):
        entity = EntityRepository.get_by_id(entity_id)
        if entity:
            EntityRepository.delete(entity)
            return True
        return False

    @staticmethod
    def get_all_entities():
        return EntitySelector.get_all()

    @staticmethod
    def get_entity_by_id(id):
        return EntitySelector.get_by_id(id)

    @staticmethod
    def get_entity_by_cpf_cnpj(cpf_cnpj):
        return EntitySelector.get_by_cpf_cnpj(cpf_cnpj)
