from shared.services import BaseService
from domains.condominium.repositories import CondominiumRepository
from domains.condominium.selectors import CondominiumSelector


class CondominiumService(BaseService):
    repository = CondominiumRepository
    selector = CondominiumSelector
