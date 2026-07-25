from shared.services import BaseService
from domains.condominium.repositories import CollaboratorRepository
from domains.condominium.selectors import CollaboratorSelector


class CollaboratorService(BaseService):
    repository = CollaboratorRepository
    selector = CollaboratorSelector
