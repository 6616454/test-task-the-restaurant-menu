from src.domain.common.exceptions.base import AppException


class RepositoryError(AppException):
    pass


class UniqueError(RepositoryError):
    pass
