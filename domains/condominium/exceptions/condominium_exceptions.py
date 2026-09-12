class CondominiumException(Exception):
    pass


class CondominiumNotFoundError(CondominiumException):
    pass


class CollaboratorException(CondominiumException):
    pass


class CollaboratorNotFoundError(CollaboratorException):
    pass


class TypesCollaboratorException(CondominiumException):
    pass


class TypesCollaboratorNotFoundError(TypesCollaboratorException):
    pass
