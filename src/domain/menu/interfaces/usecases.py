from abc import ABC

from src.domain.menu.interfaces.uow import IMenuUoW


class MenuUseCase(ABC):
    def __init__(self, uow: IMenuUoW) -> None:
        self.uow = uow


class SubMenuUseCase(MenuUseCase):
    pass


class DishUseCase(MenuUseCase):
    pass
