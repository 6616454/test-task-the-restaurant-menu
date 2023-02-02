from pydantic import Field

from src.api.handlers.responses.base import ApiError


class MenuNotFoundError(ApiError):
    detail = Field("menu not found", const=True)


class MenuAlreadyExistsError(ApiError):
    detail = Field("menu already exists", const=True)


class MenuEmptyRequestBodyError(ApiError):
    detail = Field("menu_data request body empty", const=True)


class SubMenuNotFoundError(ApiError):
    detail = Field("submenu not found", const=True)


class SubMenuAlreadyExistsError(ApiError):
    detail = Field("submenu already exists", const=True)


class SubMenuEmptyRequestBodyError(ApiError):
    detail = Field("submenu_data request body empty", const=True)


class DishNotFoundError(ApiError):
    detail = Field("dish not found", const=True)


class DishAlreadyExistsError(ApiError):
    detail = Field("dish already exists", const=True)


class DishEmptyRequestBodyError(ApiError):
    detail = Field("dish_data request body empty", const=True)


class DishPriceValidationError(ApiError):
    detail = Field("The price of the dish must be a floating point number")
