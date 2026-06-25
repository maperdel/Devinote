class DomainError(Exception):
    pass


class AlreadyExistsError(DomainError):
    pass


class InvalidCredentialsError(DomainError):
    pass


class NotFoundError(DomainError):
    pass


class IntegrityErrorExc(DomainError):
    pass


class DatabaseOperationError(DomainError):
    pass
