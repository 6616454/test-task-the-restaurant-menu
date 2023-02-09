from abc import ABC

from src.domain.common.interfaces.cache import ICache
from src.domain.menu.interfaces.uow import IMenuUoW


class MenuUseCase(ABC):
    def __init__(self, uow: IMenuUoW, cache: ICache) -> None:
        self.uow = uow
        self.cache = cache


class SubMenuUseCase(MenuUseCase):
    pass


class DishUseCase(MenuUseCase):
    pass
