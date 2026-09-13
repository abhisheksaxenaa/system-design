class ApplicationError(Exception):
    pass


class EntityNotFound(ApplicationError):
    pass


class DuplicateEntity(ApplicationError):
    pass


class InvalidOperation(ApplicationError):
    pass


class ConflictError(ApplicationError):
    pass


class IdempotencyConflict(ConflictError):
    pass