class BaseService:
    repository = None
    selector = None

    @classmethod
    def create(cls, data):
        return cls.repository.create(data)

    @classmethod
    def update(cls, entity_id, data):
        entity = cls.repository.get_by_id(entity_id)
        if entity:
            return cls.repository.update(entity, data)
        return None

    @classmethod
    def activate(cls, entity_id):
        entity = cls.repository.get_by_id(entity_id)
        if entity:
            cls.repository.update(entity, {'is_active': True})
            return True
        return False

    @classmethod
    def deactivate(cls, entity_id):
        entity = cls.repository.get_by_id(entity_id)
        if entity:
            cls.repository.update(entity, {'is_active': False})
            return True
        return False

    @classmethod
    def delete(cls, entity_id):
        entity = cls.repository.get_by_id(entity_id)
        if entity:
            cls.repository.delete(entity)
            return True
        return False

    @classmethod
    def get_details(cls, entity_id):
        return cls.selector.get_by_id(entity_id)
