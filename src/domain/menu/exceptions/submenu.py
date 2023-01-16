from src.domain.common.exceptions.base import AppException


class SubMenuException(AppException):
    """Base submenu exception"""
    pass


class SubMenuAlreadyExists(SubMenuException):
    """Submenu already exists error"""
    pass


class SubMenuNotExists(SubMenuException):
    """Submenu not exists error"""
    pass


class SubMenuDataEmpty(SubMenuException):
    """Submenu data empty error"""
    pass
