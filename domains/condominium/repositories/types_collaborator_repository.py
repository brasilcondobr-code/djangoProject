from shared.repositories import BaseRepository
from domains.condominium.models import TypesCollaborator


class TypesCollaboratorRepository(BaseRepository):
    model = TypesCollaborator
