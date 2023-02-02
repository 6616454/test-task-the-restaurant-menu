from src.domain.common.exceptions.base import AppException


class DishException(AppException):
    """Base dish exception"""

    pass


class DishAlreadyExists(DishException):
    """Dish already exists error"""

    pass


class DishNotExists(DishException):
    """Dish not exists error"""

    pass


class DishDataEmpty(DishException):
    """Dish data empty error"""

    pass
