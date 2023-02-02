from src.domain.common.exceptions.base import AppException


class MenuException(AppException):
    """Base menu exception"""

    pass


class MenuAlreadyExists(MenuException):
    """Menu already exists error"""

    pass


class MenuNotExists(MenuException):
    """Menu not exists error"""

    pass


class MenuDataEmpty(MenuException):
    """Menu data empty error"""

    pass
